"""
Утилиты для работы с аргументами командной строки и валидации.
"""

import argparse
import os


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Скачивание звуков с mixkit.co (только >10 секунд)"
    )

    parser.add_argument(
        "--download-folder",
        "-d",
        required=True,
        help="Папка для сохранения аудиофайлов",
    )
    parser.add_argument(
        "--min-files", type=int, default=50, help="Минимальное количество файлов"
    )
    parser.add_argument(
        "--max-files", type=int, default=100, help="Максимальное количество файлов"
    )

    args = parser.parse_args()

    # Валидация аргументов
    if not (50 <= args.max_files <= 1000):
        parser.error("--max-files должно быть от 50 до 1000")
    if args.min_files > args.max_files:
        parser.error("--min-files не может быть больше --max-files")

    return args


def validate_file_path(file_path: str) -> bool:
    return os.path.exists(file_path)