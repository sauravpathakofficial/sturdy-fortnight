# 🗂️ Smart File Organizer CLI

A fast, lightweight, and foolproof CLI tool that organizes cluttered directories into clean, categorized folders (e.g. PDFs into `PDFs/`, photos into `Images/`, documents into `Documents/`).

Written in pure Python 3 using standard libraries — **zero dependencies, no `pip install` required**, works seamlessly on **macOS, Linux, and Windows**.

---

## 🌟 Why Choose This?

- 🤖 **Auto-Organize (`--watch` & `--install-service`)**: Watch folders live and automatically categorize files as they appear, or install as a persistent background service on macOS.
- 🛡️ **Dry-Run Preview (`--dry-run`)**: Preview every move and summary before touching a single file.
- ⏪ **1-Click Undo (`--undo`)**: Revert any organization run back to the exact original file locations and auto-clean empty category folders.
- 🔒 **Collision-Proof**: Never overwrites existing files. If duplicates share the same name, it safely renames them (`report_1.pdf`).
- 🔄 **Recursive Support (`-r` / `--recursive`)**: Flatten and organize deeply nested subdirectories into top-level categories.
- 📦 **Zero Dependencies**: Pure Python 3 standard library. Ready to run immediately after cloning.
- ⚙️ **Customizable**: Use default mappings or pass your own custom `categories.json`.

---

## 📸 Before & After

```
BEFORE:
📁 MyFolder/
├── receipt.pdf
├── screenshot.png
├── photo.jpg
├── notes.docx
├── budget.xlsx
└── script.py

AFTER:
📁 MyFolder/
├── 📄 PDFs/
│   └── receipt.pdf
├── 🖼️ Images/
│   ├── screenshot.png
│   └── photo.jpg
├── 📝 Documents/
│   └── notes.docx
├── 📊 Spreadsheets/
│   └── budget.xlsx
└── 💻 Code/
    └── script.py
```

---

## 🚀 Quick Start (In 30 Seconds)

### 1. Clone the repository
```bash
git clone https://github.com/sauravpathakofficial/sturdy-fortnight.git
cd sturdy-fortnight
```

### 2. (Recommended) Set up a quick terminal shortcut
To use the `organize` command from anywhere on your system:

#### On macOS / Linux (zsh / bash):
```bash
echo "alias organize='python3 $(pwd)/organizer.py'" >> ~/.zshrc
source ~/.zshrc
```
*(If using bash, replace `.zshrc` with `.bashrc`)*

#### On Windows (PowerShell):
```powershell
Set-Alias organize "python $PWD\organizer.py"
```

---

## 📖 Usage Guide & Examples

### 1. Preview changes first (`--dry-run`)
Always preview to see which files will move without altering anything:
```bash
# Preview current directory
organize . --dry-run

# Preview Downloads folder
organize ~/Downloads --dry-run
```

### 2. Organize files
When you're happy with the preview, organize the folder:
```bash
# Organize current directory
organize .

# Organize Downloads folder
organize ~/Downloads
```

### 3. Organize with nested subfolders (`-r` / `--recursive`)
Include files tucked away inside nested folders:
```bash
organize ~/Downloads -r
```

### 4. Automatic Organization (Real-Time Watch Mode)
Have files organized **instantly as they land** in your folder:
```bash
# Watch Downloads folder and sort new files automatically (polls every 5s)
organize ~/Downloads --watch

# Custom check interval (e.g. every 10 seconds)
organize ~/Downloads --watch --interval 10
```
> **Smart Settle Detection**: Active downloads (`.crdownload`, `.download`, `.part`, `.tmp`) and files currently being written to are automatically skipped until download/copying is 100% complete.

### 5. Run Automatically in Background on Mac (`--install-service`)
Want it to run **permanently on its own without needing an open terminal**, even across restarts?
Install it as a native macOS LaunchAgent service:
```bash
# Set up Downloads folder to auto-organize in the background forever
organize ~/Downloads --install-service
```
- **Zero Battery & RAM Waste**: Uses Apple's native `WatchPaths` kernel events. The script stays completely turned off (0% CPU, 0 MB RAM) and is only woken up for a split-second when a new file lands, then immediately terminates.
- Check live activity log anytime:
  ```bash
  tail -f ~/.fileorganizer_Downloads.log
  ```
- To stop & remove the background service anytime:
  ```bash
  organize ~/Downloads --uninstall-service
  ```

### 6. Undo / Restore files (`--undo`)
Changed your mind or organized the wrong folder? Instantly revert:
```bash
organize ~/Downloads --undo
```
> **Note**: Files return to their exact original locations and any empty category folders created by the script are automatically removed.

### 7. Check supported categories & extensions
```bash
organize --list-categories
```

---

## 📋 Default Supported Categories

| Category | File Extensions |
|---|---|
| **PDFs** | `.pdf` |
| **Images** | `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.svg`, `.bmp`, `.ico`, `.tiff`, `.heic`, `.raw`, `.psd` |
| **Documents** | `.doc`, `.docx`, `.txt`, `.rtf`, `.odt`, `.pages`, `.md`, `.tex`, `.epub`, `.log` |
| **Spreadsheets** | `.xls`, `.xlsx`, `.csv`, `.tsv`, `.numbers`, `.ods` |
| **Presentations** | `.ppt`, `.pptx`, `.key`, `.odp` |
| **Audio** | `.mp3`, `.wav`, `.aac`, `.flac`, `.ogg`, `.m4a`, `.wma` |
| **Videos** | `.mp4`, `.mov`, `.mkv`, `.avi`, `.webm`, `.wmv`, `.flv` |
| **Archives** | `.zip`, `.tar`, `.gz`, `.tar.gz`, `.tgz`, `.rar`, `.7z`, `.bz2`, `.xz`, `.iso` |
| **Code** | `.py`, `.js`, `.ts`, `.jsx`, `.tsx`, `.html`, `.css`, `.json`, `.xml`, `.yaml`, `.yml`, `.sh`, `.cpp`, `.c`, `.java`, `.go`, `.rs`, `.sql` |
| **Installers** | `.dmg`, `.pkg`, `.app`, `.exe`, `.msi`, `.deb`, `.rpm` |

---

## ⚙️ Custom Configuration

Want custom folders or custom extensions? Create a `categories.json` file:

```json
{
  "Ebooks": [".epub", ".mobi", ".azw3"],
  "Photoshop": [".psd", ".psb"],
  "Design": [".fig", ".sketch", ".xd"]
}
```

Then run:
```bash
organize ~/Downloads --config categories.json
```

---

## 🛡️ Safety Guarantees

1. **No Overwrites**: If `report.pdf` already exists in destination, new files are saved as `report_1.pdf`, `report_2.pdf`.
2. **Ignored Files**: Hidden files (`.DS_Store`, dotfiles, `.git/`) are ignored by default.
3. **No Double-Moving**: Files already placed inside category directories are skipped to avoid redundant folder nesting.
4. **History Ledger**: Every move is recorded in `.organizer_history.json` within the target directory so it can be reliably reverted at any time.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
