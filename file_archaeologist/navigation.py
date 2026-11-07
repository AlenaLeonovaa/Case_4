
import os
from datetime import datetime
from typing import List, Dict, Any, Tuple
import utils


def get_current_drive() -> str:
    """Получение текущего диска Windows."""
    if not utils.is_windows_os():
        return ""

    cwd = os.getcwd()
    drive, _ = os.path.splitdrive(cwd)

    return drive


def list_available_drives() -> List[str]:
    """Получение списка доступных дисков Windows."""
    if not utils.is_windows_os():
        return []

    drives = []

    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        drive = f"{letter}:\\"

        if os.path.exists(drive):
            drives.append(f"{letter}:")

    return drives


def list_directory(path: str) -> Tuple[bool, List[Dict[str, Any]]]:
    """Отображение содержимого каталога в Windows."""
    if not utils.is_windows_os():
        return False, []

    if not os.path.isdir(path):
        return False, []

    items = utils.safe_windows_listdir(path)
    result = []

    for name in items:
        full_path = os.path.join(path, name)

        try:
            file_info = os.stat(full_path)
            is_dir = os.path.isdir(full_path)

            mod_time = datetime.fromtimestamp(
                file_info.st_mtime
            ).strftime("%Y-%m-%d %H:%M")

            result.append({
                "name": name,
                "type": "dir" if is_dir else "file",
                "size": 0 if is_dir else file_info.st_size,
                "modified": mod_time,
                "hidden": utils.is_hidden_windows_file(full_path)
            })

        except OSError:
            continue

    return True, result


def format_directory_output(items: List[Dict[str, Any]]) -> None:
    """Форматированный вывод содержимого каталога Windows."""
    if not items:
        print("  (пусто)")
        return

    print(
        f"{'Тип':<7} {'Размер':<10} "
        f"{'Дата изменения':<18} {'Имя'}"
    )
    print("-" * 65)

    for item in items:
        type_str = "[DIR]" if item["type"] == "dir" else "[FILE]"

        if item["type"] == "dir":
            size_str = "<DIR>"
        else:
            size_str = utils.format_size(item["size"])

        name = item["name"]

        if item["hidden"]:
            name += " [HIDDEN]"

        print(
            f"{type_str:<7} {size_str:<10} "
            f"{item['modified']:<18} {name}"
        )


def move_up(current_path: str) -> str:
    """Переход в родительский каталог Windows."""
    if not utils.is_windows_os():
        return current_path

    parent = utils.get_parent_path(current_path)

    is_valid, error_msg = utils.validate_windows_path(parent)

    if is_valid and os.path.isdir(parent):
        return parent

    if not is_valid:
        print(f"Ошибка перехода: {error_msg}")

    return current_path


def move_down(current_path: str, target_dir: str) -> Tuple[bool, str]:
    """Переход в указанный подкаталог Windows."""
    if not utils.is_windows_os():
        return False, current_path

    if not target_dir or target_dir in (".", ".."):
        return False, current_path

    if "\\" in target_dir or "/" in target_dir:
        return False, current_path

    error = utils.validate_segment(target_dir)

    if error:
        return False, current_path

    new_path = os.path.join(current_path, target_dir)

    is_valid, error_msg = utils.validate_windows_path(new_path)

    if not is_valid:
        print(f"Ошибка пути: {error_msg}")
        return False, current_path

    if not os.path.isdir(new_path):
        return False, current_path

    return True, new_path


def get_windows_special_folders() -> Dict[str, str]:
    """Получение путей к специальным папкам Windows."""
    if not utils.is_windows_os():
        return {}

    user_profile = os.environ.get("USERPROFILE")

    if not user_profile:
        return {}

    folders = {
        "Desktop": os.path.join(user_profile, "Desktop"),
        "Documents": os.path.join(user_profile, "Documents"),
        "Downloads": os.path.join(user_profile, "Downloads")
    }

    return folders

