import os
import re
import pathlib
import urllib.parse
import difflib
from typing import List, Dict, Set

# Regex for Markdown links: [text](path#anchor)
# Groups: 'path' for the file reference, 'anchor' for the section fragment
# Allows path to be empty for local anchors: (#anchor)
LINK_PATTERN = re.compile(r'\[.*?\]\((?P<path>[^#)]*)(?:#(?P<anchor>[^)]+))?\)')

# Regex for Markdown headings: # Heading Text
HEADING_PATTERN = re.compile(r'^(?P<level>#{1,6})\s+(?P<text>.+)$', re.MULTILINE)

class MarkdownLinkTester:
    def __init__(self, root_dir: str):
        self.root_dir = pathlib.Path(root_dir).resolve()
        self.heading_cache: Dict[str, List[str]] = {}

    def slugify(self, text: str) -> str:
        """
        Converts heading text into a standard Markdown anchor format.
        (Lowercase, remove special chars, replace spaces with hyphens)
        """
        text = text.lower().strip()
        # Remove non-alphanumeric characters (simplified)
        text = re.sub(r'[^\w\s\-]', '', text)
        # Replace whitespace with hyphens
        text = re.sub(r'\s+', '-', text)
        return text

    def get_headings_from_file(self, file_path: pathlib.Path) -> List[str]:
        """Extracts all headings from a file and returns them as anchor strings."""
        path_key = str(file_path)
        if path_key in self.heading_cache:
            return self.heading_cache[path_key]

        if not file_path.exists():
            return []

        try:
            content = file_path.read_text(encoding='utf-8')
            # Generate both slugified and raw-spaced versions to be safe
            slugified = [self.slugify(m.group('text')) for m in HEADING_PATTERN.finditer(content)]
            raw_text = [m.group('text').strip().replace(' ', '-') for m in HEADING_PATTERN.finditer(content)]
            
            combined = list(set(slugified + raw_text))
            self.heading_cache[path_key] = combined
            return combined
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return []

    def test_links(self):
        """Iterates through all .md files and validates internal links."""
        md_files = list(self.root_dir.rglob("*.md"))
        error_count = 0

        for md_file in md_files:
            try:
                content = md_file.read_text(encoding='utf-8')
            except Exception as e:
                print(f"Could not read file {md_file}: {e}")
                continue

            for match in LINK_PATTERN.finditer(content):
                line_number = content.count('\n', 0, match.start()) + 1
                raw_path = match.group('path') or ""
                anchor = match.group('anchor')

                # Skip external links
                if raw_path.startswith(('http://', 'https://', 'mailto:', 'ftp:')):
                    continue
                
                # If path is empty, it's a link to the current file
                if not raw_path:
                    if not anchor:
                        continue # Skip empty links like []()
                    target_path = md_file
                else:
                    # Handle missing .md extensions in links
                    processed_path = raw_path
                    if not raw_path.endswith('.md') and '.' not in os.path.basename(raw_path):
                        processed_path += '.md'

                    # Resolve target path relative to the current file
                    target_path = (md_file.parent / processed_path).resolve()

                # 1. Check if the file exists
                if not target_path.exists():
                    print(f"❌ [File Missing] in {md_file.relative_to(self.root_dir)}:{line_number}")
                    print(f"   Link: {match.group(0)}")
                    print(f"   Resolved Path: {target_path}")
                    print("-" * 40)
                    error_count += 1
                    continue

                # 2. Check if the anchor exists within the file
                if anchor:
                    decoded_anchor = urllib.parse.unquote(anchor)
                    valid_headings = self.get_headings_from_file(target_path)
                    
                    if decoded_anchor not in valid_headings:
                        print(f"⚠️  [Anchor Missing] in {md_file.relative_to(self.root_dir)}:{line_number}")
                        print(f"   Link: {match.group(0)}")
                        
                        # Suggest closest matches for potential typos
                        suggestions = difflib.get_close_matches(decoded_anchor, valid_headings, n=3, cutoff=0.5)
                        if suggestions:
                            suggestion_str = ", ".join(['#' + s for s in suggestions])
                            print(f"   Did you mean: {suggestion_str} ?")
                        else:
                            print(f"   No similar headings found in {target_path.name}.")
                        
                        print("-" * 40)
                        error_count += 1

        if error_count == 0:
            print("✅ All links are valid!")
        else:
            print(f"Done. Found {error_count} error(s).")

if __name__ == "__main__":
    # Specify your documentation directory here
    DOCS_DIRECTORY = "." 
    
    tester = MarkdownLinkTester(DOCS_DIRECTORY)
    print(f"Checking links in: {tester.root_dir}")
    md_files = list(tester.root_dir.rglob("*.md"))
    print(f"Found {len(md_files)} Markdown files.")
    tester.test_links()