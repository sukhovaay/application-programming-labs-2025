import re
from typing import List


def open_and_read(file_path: str, encoding: str = "utf-8") -> str:
    """
    Открывает и читает содержимое указанного файла.
    """
    try:
        with open(file_path, "r", encoding=encoding) as f:
            return f.read()
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Не удалось найти файл '{file_path}'.") from e
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(
            f"Невозможно декодировать файл '{file_path}' в кодировке {encoding}."
        ) from e


def save_to_file(file_path: str, content_lines: List[str], encoding: str = "utf-8") -> None:
    """
    Записывает переданный список строк в файл.
    """
    try:
        with open(file_path, "w", encoding=encoding) as f:
            for line in content_lines:
                f.write(line + "\n")
    except IOError as e:
        raise IOError(f"Произошла ошибка ввода-вывода при записи в '{file_path}'.") from e


def process_name_data(text_content: str) -> List[str]:
    """
    Обрабатывает текст, извлекает записи в формате "Фамилия: X" и "Имя: Y",
    возвращает список строк вида "X Y.".
    """
    pattern = r'Фамилия: [А-Я][а-я]+\nИмя: [А-Я][а-я]+'
    found_records = re.findall(pattern, text_content)

    formatted_results = []
    for record in found_records:
        line_surname, line_name = record.split('\n')
        surname_value = line_surname[9:]  # Удаляем префикс "Фамилия: "
        name_value = line_name[5:]        # Удаляем префикс "Имя: "
        initial = name_value[0] + '.'
        formatted_results.append(f"{surname_value} {initial}")

    return formatted_results