import os
import re
from typing import List, Dict, Any

# Импортируем модули команды
import utils
import navigation
import analysis


def find_files_windows(pattern: str, path: str, case_sensitive: bool = False) -> List[str]:
    found_files = []

    # Формируем регулярное выражение из wildcard-шаблона (* и ?)
    # Экранируем спецсимволы, затем заменяем * на .* и ? на .
    regex_pattern = re.escape(pattern).replace(r'\*', '.*').replace(r'\?', '.')
    flags = 0 if case_sensitive else re.IGNORECASE
    regex = re.compile(f"^{regex_pattern}$", flags)

    # Используем рекурсивный обход через функцию инженера
    # или стандартный os.walk, так как это поиск.
    for root, _, files in os.walk(path):
        for file in files:
            if regex.match(file):
                found_files.append(os.path.join(root, file))

    # Используем функцию аналитика для отслеживания прогресса
    analysis.count_files(path)

    return found_files


def find_by_windows_extension(extensions: List[str], path: str) -> List[str]:
    found_files = []

    # Автоматически добавляем точку, если ее нет
    clean_extensions = []
    for ext in extensions:
        if not ext.startswith('.'):
            clean_extensions.append('.' + ext.lower())
        else:
            clean_extensions.append(ext.lower())

    # Вызываем функцию аналитика для оптимизации
    # Она соберет статистику по типам, но нам нужны сами файлы
    analysis.analyze_windows_file_types(path)

    for root, _, files in os.walk(path):
        for file in files:
            _, ext = os.path.splitext(file)
            if ext.lower() in clean_extensions:
                found_files.append(os.path.join(root, file))

    return found_files


def find_large_files_windows(min_size_mb: float, path: str) -> List[Dict[str, Any]]:
    large_files = []
    min_size_bytes = min_size_mb * 1024 * 1024

    for root, _, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                # Получаем размер файла в байтах
                file_size = os.path.getsize(file_path)
                if file_size >= min_size_bytes:
                    large_files.append({
                        'path': file_path,
                        'size_mb': round(file_size / (1024 * 1024), 2),
                        'type': os.path.splitext(file)[1]
                    })
            except OSError:
                # Пропускаем файлы, к которым нет доступа
                continue

    return large_files


def find_windows_system_files(path: str) -> List[str]:
    system_files = []
    system_extensions = ['.exe', '.dll', '.sys']

    # Используем функцию навигации для получения спецпапок (по ТЗ)
    special_folders = navigation.get_windows_special_folders()

    # Ищем в переданной папке и в системных папках
    target_paths = [path]
    if 'Windows' in special_folders:
        target_paths.append(special_folders['Windows'])

    for target_path in target_paths:
        for root, _, files in os.walk(target_path):
            for file in files:
                _, ext = os.path.splitext(file)
                if ext.lower() in system_extensions:
                    system_files.append(os.path.join(root, file))

    return system_files


def format_windows_search_results(results: List[Any], search_type: str) -> None:
    if not results:
        print("Ничего не найдено.")
        return

    print(f"\n--- Результаты поиска: {search_type} ---")

    if search_type == "large_files":
        for res in results:
            # Используем format_size из utils (по ТЗ)
            size_str = utils.format_size(int(res['size_mb'] * 1024 * 1024))
            print(f"Путь: {res['path']} | Размер: {size_str} | Тип: {res['type']}")

    elif search_type == "attributes":
        # Используем get_windows_file_attributes_stats из analysis
        stats = analysis.get_windows_file_attributes_stats(results[0] if results else "")
        print(f"Статистика атрибутов: {stats}")
        for file_path in results:
            print(f"Файл: {file_path}")

    else:
        for item in results:
            print(f"- {item}")


def search_menu_handler(current_path: str) -> bool:
    print("\n=== МЕНЮ ПОИСКА ===")
    print("1. Поиск по маске (например, *.txt)")
    print("2. Поиск по расширениям (например, exe, dll)")
    print("3. Поиск крупных файлов")
    print("4. Поиск системных файлов")
    print("0. Вернуться назад")

    choice = input("Выберите действие: ")

    # Используем match case
    match choice:
        case "1":
            pattern = input("Введите маску: ")
            res = find_files_windows(pattern, current_path)
            format_windows_search_results(res, "mask")
        case "2":
            exts = input("Введите расширения через запятую: ").split(',')
            res = find_by_windows_extension(exts, current_path)
            format_windows_search_results(res, "extensions")
        case "3":
            try:
                size_mb = float(input("Введите минимальный размер в МБ: "))
                res = find_large_files_windows(size_mb, current_path)
                format_windows_search_results(res, "large_files")
            except ValueError:
                print("Ошибка: введите число.")
        case "4":
            res = find_windows_system_files(current_path)
            format_windows_search_results(res, "system_files")
        case "0":
            return False
        case _:
            print("Неверный ввод.")

    return True
