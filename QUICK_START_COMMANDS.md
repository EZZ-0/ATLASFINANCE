# 🚀 QUICK START COMMANDS

## Command 1: Run the App

### Windows:
**Just double-click:** `run_app.bat`

Or run in terminal:
```bash
run_app.bat
```

### Manual (if .bat doesn't work):
```bash
streamlit run usa_app.py
```

---

## Command 2: Export Codebase for Auditors

### Windows:
**Just double-click:** `export_codebase.bat`

Or run in terminal:
```bash
python export_codebase.py
```

### What It Does:
- ✅ Creates a complete copy of all code files
- ✅ Removes all API keys automatically
- ✅ Excludes logs, cache, and user data
- ✅ Sanitizes sensitive information
- ✅ Outputs to: `ATLAS_ENGINE_CODEBASE_EXPORT_[timestamp].txt`

### Output:
A single `.txt` file containing:
- All `.py` files (Python code)
- All `.md` files (documentation)
- All `.bat` files (scripts)
- Configuration files (`.toml`, `.yml`)
- With API keys redacted as `[GOOGLE_API_KEY_REMOVED]`

**Safe to share with:**
- Third-party auditors
- Code reviewers
- Professors
- Collaborators

---

## Files Created:

| File | Purpose |
|------|---------|
| `run_app.bat` | **Launch the app** (double-click to run) |
| `export_codebase.bat` | **Export codebase** (double-click to export) |
| `export_codebase.py` | Export script (called by .bat) |

---

## Quick Reference:

```bash
# Run the app
run_app.bat

# Export codebase for auditors
export_codebase.bat

# Or use Python directly
streamlit run usa_app.py              # Run app
python export_codebase.py             # Export code
```

---

## Notes:

- **`run_app.bat`**: Checks for Python, checks for `.env`, then launches Streamlit
- **`export_codebase.py`**: Scans all files, removes API keys, creates sanitized export
- Both are safe and non-destructive (read-only operations)

---

**🎉 Now you have one-click commands for both running and sharing the engine!**


