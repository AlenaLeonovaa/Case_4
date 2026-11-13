import os
from typing import Tuple

import navigation
import utils


def count_files(path: str) -> Tuple[bool, int]:
    """Рекурсивный подсчёт файлов в каталоге Windows."""

    visited = set()

    def count_recursive(current_path):
        real_path = os.path.normcase(os.path.realpath(current_path))

        if real_path in visited:
            return True, 0

        visited.add(real_path)

        success, items = navigation.list_directory(current_path)

        if not success:
            return False, 0

        count = 0

        for item in items:
            full_path = os.path.join(current_path, item["name"])

            if os.path.islink(full_path):
                continue

            attrs = utils.get_windows_attributes(full_path)

            if attrs == utils.INVALID_FILE_ATTRIBUTES:
                continue

            if attrs & utils.FILE_ATTRIBUTE_SYSTEM:
                continue

            if item["type"] == "file":
                count += 1

            elif item["type"] == "dir":
                sub_success, sub_count = count_recursive(full_path)

                if not sub_success:
                    return False, 0

                count += sub_count

        return True, count

    return count_recursive(path)



def count_bytes(path: str) -> Tuple[bool, int]:
    """Рекурсивный подсчёт общего размера файлов в каталоге Windows."""

    visited = set()

    def count_recursive(current_path):
        real_path = os.path.normcase(os.path.realpath(current_path))

        if real_path in visited:
            return True, 0

        visited.add(real_path)

        success, items = navigation.list_directory(current_path)

        if not success:
            return False, 0

        total_size = 0

        for item in items:
            full_path = os.path.join(current_path, item["name"])

            if os.path.islink(full_path):
                continue

            attrs = utils.get_windows_attributes(full_path)

            if attrs == utils.INVALID_FILE_ATTRIBUTES:
                continue

            if attrs & utils.FILE_ATTRIBUTE_SYSTEM:
                continue

            if item["type"] == "file":
                total_size += item["size"]

            elif item["type"] == "dir":
                sub_success, sub_size = count_recursive(full_path)

                if not sub_success:
                    return False, 0

                total_size += sub_size

        return True, total_size

    return count_recursive(path)



def analyze_windows_file_types(path: str) -> Tuple[bool, Dict[str, Dict[str, int]]]:
    """Рекурсивный анализ файлов по расширениям."""

    visited = set()

    def analyze_recursive(current_path):
        real_path = os.path.normcase(os.path.realpath(current_path))

        if real_path in visited:
            return True, {}

        visited.add(real_path)

        success, items = navigation.list_directory(current_path)

        if not success:
            return False, {}

        stats = {}

        for item in items:
            full_path = os.path.join(current_path, item["name"])

            if os.path.islink(full_path):
                continue

            attrs = utils.get_windows_attributes(full_path)

            if attrs == utils.INVALID_FILE_ATTRIBUTES:
                continue

            if attrs & utils.FILE_ATTRIBUTE_SYSTEM:
                continue

            if item["type"] == "file":
                extension = os.path.splitext(item["name"])[1].lower()

                if not extension:
                    extension = "[no extension]"

                if extension not in stats:
                    stats[extension] = {
                        "count": 0,
                        "size": 0
                    }

                stats[extension]["count"] += 1
                stats[extension]["size"] += item["size"]

            elif item["type"] == "dir":
                sub_success, sub_stats = analyze_recursive(full_path)

                if not sub_success:
                    return False, {}

                for extension, data in sub_stats.items():
                    if extension not in stats:
                        stats[extension] = {
                            "count": 0,
                            "size": 0
                        }

                    stats[extension]["count"] += data["count"]
                    stats[extension]["size"] += data["size"]

        return True, stats

    return analyze_recursive(path)

