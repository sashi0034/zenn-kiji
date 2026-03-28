import os
import re
from pathlib import Path

def extract_markdown_headers(target_dir, output_file):
    # Regex to match Markdown headers (e.g., # Header, ## Subheader)
    header_pattern = re.compile(r'^(#{1,6})\s+(.*)')
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Recursively find all .md files
        md_files = sorted(Path(target_dir).rglob('*.md'))
        
        if not md_files:
            print(f"No Markdown files found in {target_dir}")
            return

        for md_path in md_files:
            # Skip the output file if it's in the same directory
            if md_path.name == os.path.basename(output_file):
                continue
                
            outfile.write(f"[{md_path.relative_to(target_dir)}]\n\n")
            
            try:
                with open(md_path, 'r', encoding='utf-8') as infile:
                    for line in infile:
                        match = header_pattern.match(line.strip())
                        if match:
                            level = match.group(1)
                            title = match.group(2).strip().replace(' ', '-')
                            outfile.write(f"{level} {title}\n")
                
                outfile.write("\n---\n\n")  # Separator between files
            except Exception as e:
                print(f"Could not read {md_path}: {e}")

    print(f"Extraction complete! Summary saved to: {output_file}")

if __name__ == "__main__":
    # Configuration
    SEARCH_DIRECTORY = "."  # Change this to your directory
    OUTPUT_FILENAME = "extracted_sections.txt"
    
    extract_markdown_headers(SEARCH_DIRECTORY, OUTPUT_FILENAME)