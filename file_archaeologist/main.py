
from __future__ import annotations

import sys

import utils
import navigation
import analysis

try:
    import search
    SEARCH_READY = True
except ImportError:
    search = None
    SEARCH_READY = False


def _stub(module_name, action):
    """Print a message that the requested module is not ready yet."""
    print(f"[stub] module '{module_name}' is not ready "
          f"(requested action: {action})")


def check_windows_environment():
    """Exit the program if not running on Windows."""
    if not utils.is_windows_os():
        print("Error: this program requires Windows.")
        sys.exit(1)


def display_windows_banner():
    """Print the startup banner with basic environment information."""
    print("=" * 60)
    print("  FILE ARCHAEOLOGIST -- Windows filesystem navigator")
    print("=" * 60)

    try:
        drive = navigation.get_current_drive()
        print(f"  Current drive : {drive}")
    except Exception as exc:
        print(f"  Current drive : <unavailable: {exc}>")

    print("  Platform      : Windows")
    print("=" * 60)


def display_main_menu(current_path):
    """Print the current path and available commands."""
    print()
    print(f"Current path: {current_path}")
    print("-" * 60)
    print("  1. List directory / change directory")
    print("  2. Directory statistics")
    print("  3. Search")
    print("  4. Show available drives")
    print("  5. Go to parent directory")
    print("  6. Go to special folder")
    print("  0. Exit")
    print("-" * 60)


def handle_windows_navigation(command, current_path):
    """Handle navigation commands; return the (possibly new) current path."""
    if command == "1":
        ok, items = navigation.list_directory(current_path)
        if not ok:
            print("Cannot read directory.")
            return current_path
        navigation.format_directory_output(items)
        target = input("Enter subdirectory name (empty to cancel): ").strip()
        if not target:
            return current_path
        ok, new_path = navigation.move_down(current_path, target)
        if ok:
            return new_path
        print("Cannot enter that directory.")
        return current_path

    if command == "5":
        return navigation.move_up(current_path)

    if command == "6":
        folders = navigation.get_windows_special_folders()
        for name, path in folders.items():
            print(f"  {name}: {path}")
        choice = input("Enter folder name (empty to cancel): ").strip()
        if choice in folders:
            return folders[choice]
        return current_path

    print("Unknown navigation command.")
    return current_path


def handle_windows_analysis(command, current_path):
    """Handle analysis commands."""
    if command == "2":
        analysis.show_windows_directory_stats(current_path)
    else:
        print("Unknown analysis command.")


def handle_windows_search(command, current_path):
    """Handle search commands."""
    if not SEARCH_READY:
        _stub("search", command)
        return

    if command == "3":
        search.search_menu_handler(current_path)
    else:
        print("Unknown search command.")


def handle_drives():
    """Print available drives."""
    drives = navigation.list_available_drives()
    print("Available drives:")
    for d in drives:
        print(f"  {d}")


def run_windows_command(command, current_path):
    """Route a command to the right handler; return updated current path."""
    match command:
        case "0":
            print("Goodbye.")
            sys.exit(0)
        case "1" | "5" | "6":
            return handle_windows_navigation(command, current_path)
        case "2":
            handle_windows_analysis(command, current_path)
            return current_path
        case "3":
            handle_windows_search(command, current_path)
            return current_path
        case "4":
            handle_drives()
            return current_path
        case _:
            print(f"Unknown command: {command!r}")
            return current_path


def main():
    """Program entry point."""
    check_windows_environment()
    display_windows_banner()

    try:
        current_path = navigation.get_current_drive() + "\\"
    except Exception:
        current_path = "C:\\"

    while True:
        display_main_menu(current_path)
        try:
            command = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            sys.exit(0)

        current_path = run_windows_command(command, current_path)


if __name__ == "__main__":
    main()
