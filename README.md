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

## ⚡ Quick Cheat Sheet

| Goal | Command |
|---|---|
| 🚀 **Start Auto-Organizer in Background** | `python3 organizer.py ~/Downloads --start` |
| 📊 **Check Auto-Organizer Status** | `python3 organizer.py ~/Downloads --status` |
| 🛑 **Stop Background Auto-Organizer** | `python3 organizer.py ~/Downloads --stop` |
| 📜 **View Live Activity Log** | `tail -f ~/.fileorganizer_downloads.log` |
| ⏪ **Undo Last Organization** | `python3 organizer.py ~/Downloads --undo` |
| 🛡️ **Preview File Moves (Dry-Run)** | `python3 organizer.py ~/Downloads --dry-run` |
| ⚡ **One-Time Manual Organize** | `python3 organizer.py ~/Downloads` |
| 👀 **Live Foreground Watcher Mode** | `python3 organizer.py ~/Downloads --watch` |
| 📋 **List Supported Categories** | `python3 organizer.py --list-categories` |

*(If you set up the optional `organize` alias, you can replace `python3 organizer.py` with `organize`)*

---

## 📖 Usage Guide & Examples

### 1. Preview changes first (`--dry-run`)
Always preview to see which files will move without altering anything:
```bash
# Preview current directory
python3 organizer.py . --dry-run

# Preview Downloads folder
python3 organizer.py ~/Downloads --dry-run
```

### 2. Organize files manually
When you're happy with the preview, organize the folder:
```bash
# Organize current directory
python3 organizer.py .

# Organize Downloads folder
python3 organizer.py ~/Downloads
```

### 3. Organize with nested subfolders (`-r` / `--recursive`)
Include files tucked away inside nested folders:
```bash
python3 organizer.py ~/Downloads -r
```

### 4. Background Auto-Organizer (`--start`, `--status`, `--stop`)
Run the organizer automatically in the background. **You can safely close your terminal window** — it will keep running silently:

```bash
# 1. Start watching Downloads in background
python3 organizer.py ~/Downloads --start

# 2. Check if it's running & see recent activity
python3 organizer.py ~/Downloads --status

# 3. View live log of organized files
tail -f ~/.fileorganizer_downloads.log

# 4. Stop the background organizer anytime
python3 organizer.py ~/Downloads --stop
```
> **Smart Download Settle**: Active browser downloads (`.crdownload`, `.download`, `.part`, `.tmp`) are ignored while downloading. Once finished, they are instantly categorized into `PDFs/`, `Images/`, etc.

### 5. Live Foreground Watcher Mode (`--watch`)
If you prefer watching the live log directly in your terminal:
```bash
python3 organizer.py ~/Downloads --watch
```

### 6. Undo / Restore files (`--undo`)
Changed your mind or organized the wrong folder? Instantly revert:
```bash
python3 organizer.py ~/Downloads --undo
```
> **Note**: Files return to their exact original locations and any empty category folders created by the script are automatically removed.

### 7. Check supported categories & extensions
```bash
python3 organizer.py --list-categories
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
