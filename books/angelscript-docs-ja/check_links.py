import os
import re
import pathlib
import urllib.parse
import difflib
import argparse
import sys
from typing import List, Dict, Set

# Regex for Markdown links: [text](url)
# Supports one level of nested parentheses in the URL such as (co-routines)
LINK_PATTERN = re.compile(r'\[.*?\]\((?P<url>(?:[^()]+|\([^()]*\))*)\)')

# Regex for Markdown headings: # Heading Text
HEADING_PATTERN = re.compile(r'^(?P<level>#{1,6})\s+(?P<text>.+)$', re.MULTILINE)

# Zenn repository root relative to the book directory
REPO_ROOT = "../.."

class MarkdownLinkTester:
    def __init__(self, root_dir: str, repo_root: str = REPO_ROOT):
        self.root_dir = pathlib.Path(root_dir).resolve()
        # Resolve repo_root relative to the root_dir
        self.repo_root = (self.root_dir / repo_root).resolve()
        self.heading_cache: Dict[str, List[str]] = {}

    def slugify(self, text: str) -> str:
        """
        Converts heading text into a standard Markdown anchor format.
        (Lowercase, remove special chars, replace spaces with hyphens)
        """
        text = text.lower().strip()
        # Remove non-alphanumeric characters (simplified)
        # text = re.sub(r'[^\w\s\-]', '', text)
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

    def test_links(self, specific_files: List[str] = None, early_exit: bool = False, interactive: bool = False) -> int:
        """Iterates through all .md files and validates internal links."""
        if specific_files:
            md_files = []
            for f in specific_files:
                p = pathlib.Path(f).resolve()
                if p.exists() and p.suffix == '.md':
                    md_files.append(p)
                else:
                    print(f"⚠️  Warning: File not found or not a .md file: {f}")
        else:
            # Skip files with all-uppercase names (e.g., README.md, LICENSE.md, AGENTS.md)
            md_files = [f for f in self.root_dir.rglob("*.md") if not f.stem.isupper()]
        error_count = 0

        for md_file in md_files:
            if early_exit and error_count > 0:
                print("\n❌ [Early-exit] Terminating on first error.")
                return error_count

            try:
                content = md_file.read_text(encoding='utf-8')
            except Exception as e:
                print(f"Could not read file {md_file}: {e}")
                error_count += 1
                continue

            # Remove code blocks and inline code to avoid false positives
            # Replacing with spaces and preserving newlines to maintain character offsets and line numbering
            clean_content = re.sub(r'```.*?```', lambda m: re.sub(r'[^\r\n]', ' ', m.group(0)), content, flags=re.DOTALL)
            clean_content = re.sub(r'`[^`\n]+`', lambda m: ' ' * len(m.group(0)), clean_content)

            replacements = []
            for match in LINK_PATTERN.finditer(clean_content):
                line_number = content.count('\n', 0, match.start()) + 1
                url_b = match.group('url')
                if url_b and '#' in url_b:
                    parts = url_b.split('#', 1)
                    raw_path = parts[0]
                    anchor = parts[1]
                    anchor_start = match.start('url') + len(raw_path) + 1
                    anchor_end = match.end('url')
                else:
                    raw_path = url_b or ""
                    anchor = None
                    anchor_start = -1
                    anchor_end = -1

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

                    # If path starts with / or images/, treat as repo-root relative
                    if raw_path.startswith('/'):
                        target_path = (self.repo_root / raw_path.lstrip('/')).resolve()
                    elif raw_path.startswith('images/'):
                        target_path = (self.repo_root / raw_path).resolve()
                    else:
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
                            if interactive:
                                try:
                                    ans = input("   Replace? [Y/n]: ").strip().lower()
                                    if ans in ('', 'y', 'yes'):
                                        new_anchor = suggestions[0]
                                        replacements.append((anchor_start, anchor_end, new_anchor))
                                        print(f"   ✅ Replacement scheduled: #{new_anchor}")
                                except EOFError:
                                    print("   Interrupted.")
                                    return error_count
                        else:
                            print(f"   No similar headings found in {target_path.name}.")
                        
                        print("-----------------------------------------------")
                        error_count += 1

            if replacements:
                # Apply replacements in reverse order to keep offsets valid
                replacements.sort(key=lambda x: x[0], reverse=True)
                new_content = list(content)
                for start, end, rep in replacements:
                    new_content[start:end] = list(rep)
                
                try:
                    md_file.write_text("".join(new_content), encoding='utf-8')
                    print(f"📝 Fixed {len(replacements)} link(s) in {md_file.relative_to(self.root_dir)}")
                except Exception as e:
                    print(f"❌ Error writing to {md_file}: {e}")

        if error_count == 0:
            print("✅ All links are valid!")
        
        print(f"Done. Found {error_count} error(s).")
        return error_count

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate internal links in Markdown files.")
    parser.add_argument("directory", nargs="?", default=".", help="Root directory to check (default: current)")
    parser.add_argument("--early-exit", "-e", action="store_true", help="Stop immediately on the first error found.")
    parser.add_argument("--files", "-f", nargs="+", help="Specific Markdown files to check.")
    parser.add_argument("--fix", "-x", action="store_true", help="Interactively fix broken anchors with suggested corrections.")
    args = parser.parse_args()

    tester = MarkdownLinkTester(args.directory)
    print(f"Checking links in: {tester.root_dir}")
    
    # Pre-calculate file count for informational purposes
    if args.files:
        md_files_count = len(args.files)
    else:
        md_files_count = len([f for f in tester.root_dir.rglob("*.md") if not f.stem.isupper()])
    
    print(f"Found {md_files_count} Markdown files.")
    
    total_errors = tester.test_links(specific_files=args.files, early_exit=args.early_exit, interactive=args.fix)
    if total_errors > 0:
        sys.exit(1)