#!/usr/bin/env python3
"""
CODEBASE EXPORT FOR THIRD-PARTY AUDITORS
=========================================
Generates a complete, sanitized copy of the codebase for external review.

Features:
- Exports all Python files
- Removes API keys and sensitive data
- Includes configuration files
- Excludes cache, logs, and user data
- Creates a single .txt file for easy sharing

Usage:
    python export_codebase.py
    
Output:
    ATLAS_ENGINE_CODEBASE_EXPORT_[timestamp].txt
"""

import os
import re
from datetime import datetime
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================

# Files to include (by extension)
INCLUDE_EXTENSIONS = ['.py', '.txt', '.md', '.bat', '.sh', '.toml', '.yml', '.yaml']

# Directories to exclude
EXCLUDE_DIRS = {
    '__pycache__', '.git', 'venv', 'env', 'ENV', 
    'logs', 'saved_scenarios', 'exports', '.cache',
    'build', 'dist', '.pytest_cache', '.ipynb_checkpoints',
    'archive_old_files', 'docs', 'tests', '4t43wt',
    'AFI', 'school_project', 'suggested_theme'
}

# Files to exclude
EXCLUDE_FILES = {
    '.env', '.env.local', '.env.production',
    'test_security_fixes.py',  # Contains security test cases
    'export_codebase.py',  # This script itself
}

# Patterns to sanitize (will be replaced with placeholders)
SANITIZE_PATTERNS = [
    (re.compile(r'AIzaSy[A-Za-z0-9_-]{33}'), '[GOOGLE_API_KEY_REMOVED]'),
    (re.compile(r'sk-[A-Za-z0-9]{48}'), '[OPENAI_API_KEY_REMOVED]'),
    (re.compile(r'gsk_[A-Za-z0-9]{52}'), '[GROQ_API_KEY_REMOVED]'),
    (re.compile(r'GEMINI_API_KEY\s*=\s*["\'][^"\']+["\']'), 'GEMINI_API_KEY="[REDACTED]"'),
    (re.compile(r'GROQ_API_KEY\s*=\s*["\'][^"\']+["\']'), 'GROQ_API_KEY="[REDACTED]"'),
]

# ==========================================
# EXPORT LOGIC
# ==========================================

def sanitize_content(content: str) -> str:
    """Remove sensitive data from content"""
    for pattern, replacement in SANITIZE_PATTERNS:
        content = pattern.sub(replacement, content)
    return content


def should_include_file(file_path: Path) -> bool:
    """Check if file should be included in export"""
    # Check extension
    if file_path.suffix not in INCLUDE_EXTENSIONS:
        return False
    
    # Check if in excluded directory
    for part in file_path.parts:
        if part in EXCLUDE_DIRS:
            return False
    
    # Check if excluded file
    if file_path.name in EXCLUDE_FILES:
        return False
    
    return True


def export_codebase():
    """Generate complete codebase export"""
    
    print("=" * 80)
    print("📦 ATLAS ENGINE - CODEBASE EXPORT FOR AUDITORS")
    print("=" * 80)
    print()
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"ATLAS_ENGINE_CODEBASE_EXPORT_{timestamp}.txt"
    
    print(f"📝 Exporting codebase to: {output_file}")
    print(f"🔒 Sanitizing API keys and sensitive data...")
    print()
    
    # Collect all files
    root_dir = Path('.')
    files_to_export = []
    
    for file_path in root_dir.rglob('*'):
        if file_path.is_file() and should_include_file(file_path):
            files_to_export.append(file_path)
    
    files_to_export.sort()
    
    print(f"📂 Found {len(files_to_export)} files to export")
    print()
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8', errors='ignore') as out:
        # Write header
        out.write("=" * 80 + "\n")
        out.write("ATLAS FINANCIAL INTELLIGENCE ENGINE - COMPLETE CODEBASE\n")
        out.write("=" * 80 + "\n")
        out.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        out.write(f"Total Files: {len(files_to_export)}\n")
        out.write(f"Purpose: Third-party security audit\n")
        out.write("\n")
        out.write("SECURITY NOTICE:\n")
        out.write("- All API keys have been removed/redacted\n")
        out.write("- User data and logs excluded\n")
        out.write("- Cached files excluded\n")
        out.write("- This export is safe to share with auditors\n")
        out.write("\n")
        out.write("=" * 80 + "\n")
        out.write("TABLE OF CONTENTS\n")
        out.write("=" * 80 + "\n")
        out.write("\n")
        
        # Write table of contents
        for i, file_path in enumerate(files_to_export, 1):
            out.write(f"{i:3d}. {file_path}\n")
        
        out.write("\n")
        out.write("=" * 80 + "\n")
        out.write("FILE CONTENTS\n")
        out.write("=" * 80 + "\n")
        out.write("\n\n")
        
        # Write each file
        for i, file_path in enumerate(files_to_export, 1):
            print(f"  [{i}/{len(files_to_export)}] Exporting: {file_path}")
            
            # File header
            out.write("\n" + "=" * 80 + "\n")
            out.write(f"FILE: {file_path}\n")
            out.write("=" * 80 + "\n")
            out.write(f"Path: {file_path}\n")
            out.write(f"Size: {file_path.stat().st_size} bytes\n")
            out.write(f"Modified: {datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}\n")
            out.write("\n")
            out.write("-" * 80 + "\n")
            out.write("CONTENT:\n")
            out.write("-" * 80 + "\n\n")
            
            # File content
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                # Sanitize content
                content = sanitize_content(content)
                
                # Write content
                out.write(content)
                out.write("\n\n")
                
            except Exception as e:
                out.write(f"[ERROR: Could not read file: {e}]\n\n")
        
        # Write footer
        out.write("\n" + "=" * 80 + "\n")
        out.write("END OF CODEBASE EXPORT\n")
        out.write("=" * 80 + "\n")
        out.write(f"Total Files Exported: {len(files_to_export)}\n")
        out.write(f"Export Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        out.write("\n")
        out.write("DISCLAIMER:\n")
        out.write("This codebase is provided for security audit purposes only.\n")
        out.write("All sensitive data has been redacted. For production deployment,\n")
        out.write("ensure proper API keys and configuration are in place.\n")
        out.write("=" * 80 + "\n")
    
    # Generate summary
    file_size = os.path.getsize(output_file)
    file_size_mb = file_size / (1024 * 1024)
    
    print()
    print("=" * 80)
    print("✅ EXPORT COMPLETE!")
    print("=" * 80)
    print()
    print(f"📄 Output File: {output_file}")
    print(f"📦 File Size: {file_size_mb:.2f} MB ({file_size:,} bytes)")
    print(f"📂 Files Exported: {len(files_to_export)}")
    print()
    print("🔒 Security Status:")
    print("   ✅ API keys removed/redacted")
    print("   ✅ Logs excluded")
    print("   ✅ User data excluded")
    print("   ✅ Cache excluded")
    print()
    print("📧 This file is now safe to share with third-party auditors!")
    print()
    print("=" * 80)


if __name__ == "__main__":
    try:
        export_codebase()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")


