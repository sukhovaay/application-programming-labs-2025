import argparse
import os
import sys

def parse_command_line_args() -> argparse.Namespace:
    """
    Парсинг аргументов командной строки.
    
    Ожидает два аргумента:
    - input_file_path: путь к исходному аудиофайлу
    - output_file_path: путь для сохранения результата
    """
    parser = argparse.ArgumentParser(
        description="Обработка аудио: переворачивание аудиофайла задом наперед"
    )
    parser.add_argument(
        "input_file_path", 
        help="Путь к входному аудиофайлу"
    )
    parser.add_argument(
        "output_file_path", 
        help="Путь для сохранения обработанного аудиофайла"
    )

    parsed_args = parser.parse_args()

    # Проверка существования входного файла
    if not os.path.exists(parsed_args.input_file_path):
        print(f"Ошибка: файл '{parsed_args.input_file_path}' не найден.")
        print(f"Текущая рабочая директория: {os.getcwd()}")
        sys.exit(1)

    # Проверка и предупреждение о форматах файлов
    input_file_extension = os.path.splitext(parsed_args.input_file_path)[1].lower()
    supported_extensions = [".wav", ".flac", ".ogg", ".aiff"]
    
    if input_file_extension not in supported_extensions:
        print("Внимание: SoundFile лучше всего работает с форматами WAV, FLAC, OGG.")
        print("Для MP3 файлов рекомендуется предварительная конвертация в WAV.")
        print("Продолжаем обработку...")

    return parsed_args