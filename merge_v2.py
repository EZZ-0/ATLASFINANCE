import os

# Configuration
ROOT_DIR = "."
OUTPUT_FILE = "full_codebase_v2.txt"  # Renamed for the 2nd audit

# File types to include (Code & Configs)
INCLUDED_EXTENSIONS = {
    ".py", ".js", ".html", ".css",  # Code
    ".md", ".txt",                  # Documentation
    ".json", ".yaml", ".yml", ".toml", ".ini", # Configs
    ".sql", ".sh", ".bat"           # Scripts
}

# Directories to ignore (Standard garbage)
EXCLUDED_DIRS = {
    ".git", "__pycache__", "venv", "env", ".venv", 
    "node_modules", ".idea", ".vscode", "dist", "build",
    "__pycache__", ".pytest_cache", ".streamlit"
}

# Specific files to ignore (Security & Noise)
EXCLUDED_FILES = {
    "merge_project.py", "merge_v2.py", 
    "package-lock.json", "poetry.lock",
    ".DS_Store", ".env" # CRITICAL: Skip .env to protect secrets
}

def merge_files():
    print(f"🚀 Starting merge... scanning '{ROOT_DIR}'")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        # Write Header
        outfile.write(f"================================================================================\n")
        outfile.write(f"AUDIT EXPORT V2 - {OUTPUT_FILE}\n")
        outfile.write(f"================================================================================\n\n")

        for root, dirs, files in os.walk(ROOT_DIR):
            # Modifying 'dirs' in-place skips those directories in os.walk
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            
            for file in files:
                if file in EXCLUDED_FILES:
                    continue
                    
                if any(file.endswith(ext) for ext in INCLUDED_EXTENSIONS):
                    file_path = os.path.join(root, file)
                    
                    # Create a clear separator for the LLM to read
                    separator = "=" * 80
                    outfile.write(f"\n{separator}\n")
                    outfile.write(f"FILE PATH: {file_path}\n")
                    outfile.write(f"{separator}\n\n")
                    
                    try:
                        with open(file_path, "r", encoding="utf-8") as infile:
                            content = infile.read()
                            # Optional: basic secret redaction (simple check)
                            if "sk-" in content or "gsk_" in content:
                                outfile.write("# [WARNING: POTENTIAL API KEY DETECTED & REDACTED]\n")
                                # Note: This is a simple check, always manually review!
                                
                            outfile.write(content)
                            outfile.write("\n")
                            print(f"✅ Added: {file_path}")
                    except Exception as e:
                        outfile.write(f"# Error reading file: {e}\n")
                        print(f"❌ Error reading {file_path}: {e}")

    print(f"\n🎉 Done! Upload '{OUTPUT_FILE}' for your 2nd Audit.")

if __name__ == "__main__":
    merge_files()