import os

# Configuration
ROOT_DIR = "."
OUTPUT_FILE = "full_codebase.txt"
# Add extensions you want to include
INCLUDED_EXTENSIONS = {".py", ".md", ".txt", ".json", ".yaml", ".yml", ".toml"}
# Add directories you want to exclude
EXCLUDED_DIRS = {".git", "__pycache__", "venv", "env", "node_modules", ".idea", ".vscode"}

def merge_files():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        for root, dirs, files in os.walk(ROOT_DIR):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            
            for file in files:
                if any(file.endswith(ext) for ext in INCLUDED_EXTENSIONS):
                    file_path = os.path.join(root, file)
                    # Create a header for each file
                    separator = "=" * 50
                    outfile.write(f"\n{separator}\n")
                    outfile.write(f"FILE: {file_path}\n")
                    outfile.write(f"{separator}\n\n")
                    
                    try:
                        with open(file_path, "r", encoding="utf-8") as infile:
                            outfile.write(infile.read())
                            outfile.write("\n")
                    except Exception as e:
                        outfile.write(f"# Error reading file: {e}\n")

    print(f"✅ Success! All files merged into '{OUTPUT_FILE}'")

if __name__ == "__main__":
    merge_files()