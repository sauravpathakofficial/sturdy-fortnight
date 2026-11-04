# Smart File Organizer CLI

A fast, lightweight, and safe CLI tool for organizing cluttered folders into clean, categorized directories (e.g. PDFs into `PDFs/`, Images into `Images/`, etc.).

Written in pure Python 3 using standard libraries — **zero external pip dependencies required**.

---

## Features

- **Automatic Categorization**: Pre-configured categories for PDFs, Images, Documents, Spreadsheets, Presentations, Audio, Videos, Archives, Code, and Installers.
- **Dry-Run Preview (`--dry-run`)**: Inspect exactly what moves will occur before any file is touched.
- **Full Undo / Restore (`--undo`)**: Easily revert the entire operation back to original file locations.
- **Collision Safe**: If duplicate names exist, appends `_1`, `_2` so existing files are never overwritten.
- **Recursive Sorting (`-r` / `--recursive`)**: Clean files across subdirectories into organized top-level category folders.
- **Custom Categories (`--config`)**: Override or add categories using a custom JSON file.

---

## Installation & Setup

The tool is located at:
```bash
/Users/saurav/.gemini/antigravity-ide/scratch/file-organizer/organizer.py
```

### (Optional) Create a global terminal shortcut
To run it from anywhere in your terminal:
```bash
echo 'alias organize="python3 /Users/saurav/.gemini/antigravity-ide/scratch/file-organizer/organizer.py"' >> ~/.zshrc
source ~/.zshrc
```

---

## Usage Guide

### 1. View default categories and supported extensions
```bash
python3 organizer.py --list-categories
```

### 2. Preview changes safely (Dry Run)
Before moving anything, run `--dry-run` to see what files will be organized:
```bash
# Preview current directory
python3 organizer.py --dry-run

# Preview a specific directory (e.g., Downloads)
python3 organizer.py ~/Downloads --dry-run
```

### 3. Organize files
```bash
# Organize current directory
python3 organizer.py

# Organize specific directory
python3 organizer.py ~/Downloads
```

### 4. Organize recursively (including subfolders)
```bash
python3 organizer.py ~/Downloads -r
```

### 5. Undo the last organization
If you want to revert files back to their original spots:
```bash
python3 organizer.py ~/Downloads --undo
```
*Note: Empty category folders created by the organizer are automatically cleaned up on undo.*

### 6. Using a custom categories config
```bash
python3 organizer.py ~/Downloads --config categories.json
```
