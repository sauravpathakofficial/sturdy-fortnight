#!/usr/bin/env python3
"""
File Organizer CLI Tool
Organizes files into categorized folders (PDFs, Images, Documents, etc.)
with dry-run preview, undo/restore support, recursive sorting, and safe collision handling.
"""

import os
import sys
import time
import json
import shutil
import argparse
import re
import subprocess
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Extensions to ignore during scan (in-progress downloads or temporary editor files)
INCOMPLETE_EXTENSIONS = {".crdownload", ".download", ".part", ".tmp", ".swp", ".crswap"}

# Default extension to folder mappings
DEFAULT_CATEGORIES = {
    "PDFs": [".pdf"],
    "Images": [
        ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp",
        ".ico", ".tiff", ".tif", ".heic", ".raw", ".psd", ".ai"
    ],
    "Documents": [
        ".doc", ".docx", ".txt", ".rtf", ".odt", ".pages", ".md",
        ".tex", ".epub", ".log"
    ],
    "Spreadsheets": [
        ".xls", ".xlsx", ".csv", ".tsv", ".numbers", ".ods"
    ],
    "Presentations": [
        ".ppt", ".pptx", ".key", ".odp"
    ],
    "Audio": [
        ".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a", ".wma", ".aiff"
    ],
    "Videos": [
        ".mp4", ".mov", ".mkv", ".avi", ".webm", ".wmv", ".flv", ".m4v"
    ],
    "Archives": [
        ".zip", ".tar", ".gz", ".tar.gz", ".tgz", ".rar", ".7z",
        ".bz2", ".xz", ".iso"
    ],
    "Code": [
        ".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".json",
        ".xml", ".yaml", ".yml", ".sh", ".bash", ".zsh", ".c", ".cpp",
        ".h", ".hpp", ".java", ".rs", ".go", ".sql", ".php", ".rb"
    ],
    "Installers": [
        ".dmg", ".pkg", ".app", ".exe", ".msi", ".deb", ".rpm"
    ]
}

HISTORY_FILENAME = ".organizer_history.json"

# ANSI Terminal Colors
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[32m"
    CYAN = "\033[36m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"

def colorize(text, color):
    if sys.stdout.isatty():
        return f"{color}{text}{Colors.RESET}"
    return text

def build_extension_lookup(categories):
    lookup = {}
    for folder, extensions in categories.items():
        for ext in extensions:
            lookup[ext.lower()] = folder
    return lookup

def load_categories(config_path=None):
    categories = dict(DEFAULT_CATEGORIES)
    if config_path and Path(config_path).is_file():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                user_cfg = json.load(f)
                if isinstance(user_cfg, dict):
                    categories.update(user_cfg)
        except Exception as e:
            print(colorize(f"Warning: Failed to load config file {config_path}: {e}", Colors.YELLOW))
    return categories

def get_history_file(target_dir: Path) -> Path:
    return target_dir / HISTORY_FILENAME

def load_history(target_dir: Path):
    history_file = get_history_file(target_dir)
    if history_file.exists():
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(target_dir: Path, history_entry):
    history = load_history(target_dir)
    history.append(history_entry)
    history_file = get_history_file(target_dir)
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

def get_unique_destination(dest_dir: Path, filename: str) -> Path:
    dest_path = dest_dir / filename
    if not dest_path.exists():
        return dest_path

    stem = Path(filename).stem
    suffix = Path(filename).suffix
    counter = 1

    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_dest = dest_dir / new_name
        if not new_dest.exists():
            return new_dest
        counter += 1

def collect_files(target_dir: Path, categories: dict, recursive: bool = False):
    category_folder_names = set(categories.keys())
    target_abs = target_dir.resolve()
    files_to_process = []

    if recursive:
        iterator = target_abs.rglob("*")
    else:
        iterator = target_abs.glob("*")

    for p in iterator:
        # Only process regular files
        if not p.is_file():
            continue

        # Ignore hidden files, system files, and the history file
        if p.name.startswith(".") or p.name == HISTORY_FILENAME:
            continue

        # Ignore in-progress downloads and temporary swap files
        name_lower = p.name.lower()
        if any(name_lower.endswith(ext) for ext in INCOMPLETE_EXTENSIONS):
            continue

        # Prevent moving files already located directly within any category directory
        relative_parents = p.resolve().relative_to(target_abs).parts[:-1]
        if any(part in category_folder_names for part in relative_parents):
            continue

        files_to_process.append(p.resolve())

    return files_to_process

def organize_files(target_dir: Path, categories: dict, recursive: bool = False, dry_run: bool = False, silent_if_empty: bool = False) -> int:
    target_dir = target_dir.resolve()
    if not target_dir.is_dir():
        print(colorize(f"Error: Target directory does not exist: {target_dir}", Colors.RED))
        sys.exit(1)

    ext_lookup = build_extension_lookup(categories)
    files = collect_files(target_dir, categories, recursive=recursive)

    if not files:
        if not silent_if_empty:
            print(colorize("No loose or unorganized files found to categorize.", Colors.YELLOW))
        return 0

    # Plan moves
    planned_moves = []
    category_counts = defaultdict(int)
    unmatched_files = []

    for file_path in files:
        # Check double extensions like .tar.gz first
        ext = "".join(file_path.suffixes).lower()
        folder = ext_lookup.get(ext)
        if not folder:
            # Fallback to standard last suffix
            ext = file_path.suffix.lower()
            folder = ext_lookup.get(ext)

        if folder:
            category_counts[folder] += 1
            dest_dir = target_dir / folder
            planned_moves.append((file_path, dest_dir))
        else:
            unmatched_files.append(file_path)

    # Print summary of plan
    print(colorize(f"\n📁 Target Directory: {target_dir}", Colors.BOLD))
    print(colorize(f"🔍 Mode: {'RECURSIVE' if recursive else 'SHALLOW'}", Colors.CYAN))
    print(colorize(f"⚡ Status: {'[DRY-RUN PREVIEW - NO CHANGES MADE]' if dry_run else '[LIVE EXECUTION]'}\n", Colors.MAGENTA if dry_run else Colors.GREEN))

    if planned_moves:
        print(colorize("Planned Categorization Summary:", Colors.BOLD))
        for cat, count in sorted(category_counts.items()):
            print(f"  • {colorize(cat, Colors.CYAN)}: {count} file{'s' if count > 1 else ''}")
        print()

    if dry_run:
        print(colorize("Preview of planned moves:", Colors.BOLD))
        for src, dest_dir in planned_moves:
            rel_src = src.relative_to(target_dir)
            target_dest = dest_dir / src.name
            print(f"  {colorize(str(rel_src), Colors.DIM)}  ➜  {colorize(str(dest_dir.name) + '/' + target_dest.name, Colors.GREEN)}")
        if unmatched_files:
            print(colorize(f"\nSkipped {len(unmatched_files)} file(s) with unrecognized extensions (leave untouched):", Colors.YELLOW))
            for f in unmatched_files[:10]:
                print(f"  - {f.name}")
            if len(unmatched_files) > 10:
                print(f"  ... and {len(unmatched_files) - 10} more.")
        print(colorize("\n✨ Dry run complete. Run without --dry-run to apply changes.", Colors.BOLD))
        return len(planned_moves)

    # Live Execution
    executed_ops = []
    for src, dest_dir in planned_moves:
        dest_dir.mkdir(parents=True, exist_ok=True)
        final_dest = get_unique_destination(dest_dir, src.name)
        
        try:
            shutil.move(str(src), str(final_dest))
            executed_ops.append({
                "source": str(src),
                "destination": str(final_dest)
            })
            rel_src = src.name if src.parent == target_dir else str(src.relative_to(target_dir))
            print(f"  {colorize('✔ Moved:', Colors.GREEN)} {rel_src} ➜ {colorize(str(dest_dir.name) + '/' + final_dest.name, Colors.CYAN)}")
        except Exception as e:
            print(colorize(f"  ✖ Failed to move {src.name}: {e}", Colors.RED))

    # Save to history for undo
    if executed_ops:
        history_entry = {
            "run_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "timestamp": datetime.now().isoformat(),
            "target_dir": str(target_dir),
            "operations": executed_ops
        }
        save_history(target_dir, history_entry)
        print(colorize(f"\n🎉 Successfully organized {len(executed_ops)} file(s)!", Colors.GREEN + Colors.BOLD))
        print(colorize(f"💡 You can undo this operation anytime by running: python3 organizer.py \"{target_dir}\" --undo\n", Colors.DIM))

    return len(executed_ops)

def undo_last_operation(target_dir: Path):
    target_dir = target_dir.expanduser().resolve()
    history = load_history(target_dir)

    if not history:
        print(colorize(f"No previous organization history found in {target_dir}.", Colors.YELLOW))
        return

    last_run = history.pop()
    operations = last_run.get("operations", [])
    print(colorize(f"\n⏪ Reverting run from {last_run.get('timestamp')} ({len(operations)} files)...", Colors.BOLD))

    reverted_count = 0
    dirs_to_check = set()

    for op in reversed(operations):
        src = Path(op["source"])
        dest = Path(op["destination"])

        if not dest.exists():
            print(colorize(f"  ✖ Warning: {dest.name} is missing, skipping.", Colors.YELLOW))
            continue

        # Ensure parent folder for original source exists
        src.parent.mkdir(parents=True, exist_ok=True)
        final_source = get_unique_destination(src.parent, src.name)

        try:
            shutil.move(str(dest), str(final_source))
            dirs_to_check.add(dest.parent)
            reverted_count += 1
            print(f"  {colorize('✔ Restored:', Colors.GREEN)} {dest.name} ➜ {colorize(str(final_source.relative_to(target_dir)), Colors.CYAN)}")
        except Exception as e:
            print(colorize(f"  ✖ Failed to restore {dest.name}: {e}", Colors.RED))

    # Clean up empty category directories if they were left empty
    for d in dirs_to_check:
        try:
            if d.is_dir() and not any(d.iterdir()):
                d.rmdir()
                print(colorize(f"  🗑 Removed empty folder: {d.name}/", Colors.DIM))
        except Exception:
            pass

    # Save updated history
    history_file = get_history_file(target_dir)
    if history:
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
    else:
        if history_file.exists():
            history_file.unlink()

    print(colorize(f"\n✨ Undo completed! Restored {reverted_count} file(s).\n", Colors.GREEN + Colors.BOLD))

def list_categories(categories):
    print(colorize("\n📋 Supported File Categories & Extensions:\n", Colors.BOLD))
    for folder, extensions in sorted(categories.items()):
        ext_list = ", ".join(extensions)
        print(f"  {colorize(folder.ljust(15), Colors.CYAN)} : {ext_list}")
    print()

def watch_directory(target_dir: Path, categories: dict, recursive: bool = False, interval: int = 5):
    target_dir = target_dir.expanduser().resolve()
    if not target_dir.is_dir():
        print(colorize(f"Error: Target directory does not exist: {target_dir}", Colors.RED))
        sys.exit(1)

    print(colorize("\n👀 Auto-Organizer Active (Watch Mode)", Colors.BOLD + Colors.GREEN))
    print(f"  • Watching folder: {colorize(str(target_dir), Colors.CYAN)}")
    print(f"  • Scan interval  : every {colorize(str(interval) + 's', Colors.BOLD)}")
    print(f"  • Mode           : {colorize('RECURSIVE' if recursive else 'SHALLOW', Colors.CYAN)}")
    print(colorize(f"  • Press {colorize('Ctrl+C', Colors.YELLOW)} at any time to exit.\n", Colors.DIM))

    try:
        while True:
            # Check for candidate files
            files = collect_files(target_dir, categories, recursive=recursive)
            if files:
                # Settle check: ensure files aren't actively being downloaded or written to
                initial_sizes = {}
                for f in files:
                    try:
                        initial_sizes[f] = f.stat().st_size
                    except (FileNotFoundError, PermissionError):
                        pass

                # Short wait to detect changes in byte size
                time.sleep(1.5)

                ready_files = []
                for f, prev_size in initial_sizes.items():
                    try:
                        if f.exists() and f.stat().st_size == prev_size:
                            ready_files.append(f)
                    except (FileNotFoundError, PermissionError):
                        pass

                if ready_files:
                    moved = organize_files(target_dir, categories, recursive=recursive, dry_run=False, silent_if_empty=True)
                    if moved > 0:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(colorize(f"[{timestamp}] ⚡ Auto-organized {moved} file(s). Waiting for next files...", Colors.GREEN + Colors.BOLD))

            time.sleep(interval)
    except KeyboardInterrupt:
        print(colorize("\n\n👋 Stopped watching. Goodbye!\n", Colors.CYAN + Colors.BOLD))
        sys.exit(0)

def get_service_label(target_dir: Path) -> str:
    target_abs = target_dir.expanduser().resolve()
    folder_slug = re.sub(r"[^a-zA-Z0-9_]", "_", target_abs.name).lower()
    return f"com.fileorganizer.{folder_slug}"

def get_plist_path(label: str) -> Path:
    launch_agents = Path.home() / "Library" / "LaunchAgents"
    launch_agents.mkdir(parents=True, exist_ok=True)
    return launch_agents / f"{label}.plist"

def install_service(target_dir: Path, recursive: bool = False, interval: int = 5):
    if sys.platform != "darwin":
        print(colorize("Auto-start service install is currently configured for macOS launchd.", Colors.YELLOW))
        print("For Linux, consider setting up a systemd user service or crontab.")
        return

    target_dir = target_dir.expanduser().resolve()
    if not target_dir.is_dir():
        print(colorize(f"Error: Target directory does not exist: {target_dir}", Colors.RED))
        sys.exit(1)

    label = get_service_label(target_dir)
    plist_path = get_plist_path(label)
    python_bin = sys.executable
    script_path = str(Path(__file__).resolve())
    log_file = Path.home() / f".fileorganizer_{target_dir.name}.log"

    recursive_arg = "        <string>-r</string>\n" if recursive else ""

    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{label}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_bin}</string>
        <string>{script_path}</string>
        <string>{str(target_dir)}</string>
        <string>--event-trigger</string>
{recursive_arg}    </array>
    <key>WatchPaths</key>
    <array>
        <string>{str(target_dir)}</string>
    </array>
    <key>ThrottleInterval</key>
    <integer>10</integer>
    <key>StandardOutPath</key>
    <string>{str(log_file)}</string>
    <key>StandardErrorPath</key>
    <string>{str(log_file)}</string>
</dict>
</plist>
"""
    # Unload first if previously active
    if plist_path.exists():
        subprocess.run(["launchctl", "unload", str(plist_path)], capture_output=True)

    with open(plist_path, "w", encoding="utf-8") as f:
        f.write(plist_content.strip() + "\n")

    res = subprocess.run(["launchctl", "load", str(plist_path)], capture_output=True, text=True)
    if res.returncode == 0:
        print(colorize("\n🚀 Zero-Battery Event Trigger Successfully Installed & Activated!", Colors.GREEN + Colors.BOLD))
        print(f"  • Service Label : {colorize(label, Colors.CYAN)}")
        print(f"  • Watching      : {colorize(str(target_dir), Colors.BOLD)}")
        print(f"  • Energy Impact : {colorize('0% idle CPU & 0 MB RAM (macOS wakes script only when a file lands)', Colors.GREEN)}")
        print(f"  • Activity Log  : {colorize(str(log_file), Colors.DIM)}")
        print(f"  • Plist Config  : {colorize(str(plist_path), Colors.DIM)}")
        print(colorize("\n✨ Whenever a file drops into this folder, macOS wakes the script for a split-second to categorize it, then immediately quits!", Colors.BOLD))
        print(colorize(f"\n💡 View activity logs anytime with:\n  tail -f \"{log_file}\"", Colors.DIM))
        print(colorize(f"\n💡 To stop and uninstall this anytime:\n  python3 {Path(__file__).name} \"{target_dir}\" --uninstall-service\n", Colors.YELLOW))
    else:
        print(colorize(f"Failed to load service with launchctl: {res.stderr}", Colors.RED))

def uninstall_service(target_dir: Path):
    if sys.platform != "darwin":
        print(colorize("Service uninstall is configured for macOS launchd.", Colors.YELLOW))
        return

    target_dir = target_dir.expanduser().resolve()
    label = get_service_label(target_dir)
    plist_path = get_plist_path(label)

    if not plist_path.exists():
        print(colorize(f"No background service found for {target_dir} ({plist_path.name} not found).", Colors.YELLOW))
        return

    subprocess.run(["launchctl", "unload", str(plist_path)], capture_output=True)
    try:
        plist_path.unlink()
        print(colorize(f"\n🛑 Successfully stopped and removed background service: {label}", Colors.GREEN + Colors.BOLD))
        print(colorize("The folder will no longer be monitored in the background.\n", Colors.DIM))
    except Exception as e:
        print(colorize(f"Error removing plist file: {e}", Colors.RED))

def main():
    parser = argparse.ArgumentParser(
        description="Smart File Organizer: Categorize files into organized folders with preview, undo, and real-time auto-watch."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Path to the directory to organize (default: current directory)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview file moves without actually moving any files"
    )
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Recursively scan and organize files in subdirectories"
    )
    parser.add_argument(
        "--undo",
        action="store_true",
        help="Undo the last organization operation in the target directory"
    )
    parser.add_argument(
        "-w", "--watch",
        action="store_true",
        help="Continuously monitor the folder and automatically organize new files as they land"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Polling interval in seconds for --watch mode (default: 5)"
    )
    parser.add_argument(
        "--install-service",
        action="store_true",
        help="Install & start a persistent macOS background LaunchAgent (auto-runs on boot/login)"
    )
    parser.add_argument(
        "--uninstall-service",
        action="store_true",
        help="Stop and remove the persistent macOS background LaunchAgent"
    )
    parser.add_argument(
        "--event-trigger",
        action="store_true",
        help=argparse.SUPPRESS
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to custom JSON file containing category definitions"
    )
    parser.add_argument(
        "--list-categories",
        action="store_true",
        help="Show currently configured categories and their file extensions"
    )

    args = parser.parse_args()

    categories = load_categories(args.config)

    if args.list_categories:
        list_categories(categories)
        return

    target_dir = Path(args.directory).expanduser()

    if args.event_trigger:
        time.sleep(1.0)
        moved = organize_files(target_dir, categories, recursive=args.recursive, dry_run=False, silent_if_empty=True)
        if moved > 0:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(colorize(f"[{timestamp}] ⚡ Auto-organized {moved} file(s) via macOS event trigger.", Colors.GREEN))
        return

    if args.install_service:
        install_service(target_dir, recursive=args.recursive, interval=args.interval)
        return

    if args.uninstall_service:
        uninstall_service(target_dir)
        return

    if args.undo:
        undo_last_operation(target_dir)
    elif args.watch:
        watch_directory(target_dir, categories, recursive=args.recursive, interval=args.interval)
    else:
        organize_files(target_dir, categories, recursive=args.recursive, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
