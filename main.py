"""
Основной модуль программы.
Координирует скачивание звуков и демонстрирует работу итератора.
"""

import os
from utils import parse_arguments
from downloader import SoundDownloader
from iterator import SoundIterator


def main():
    args = parse_arguments()

    # Скачивание звуков
    downloader = SoundDownloader()
    annotation_path = downloader.download_sounds(
        download_folder=args.download_folder,
        min_files=args.min_files,
        max_files=args.max_files,
        min_duration=10,
    )

    # Демонстрация работы итератора
    if annotation_path and os.path.exists(annotation_path):
        print("\n" + "=" * 50)
        print("Демонстрация работы итератора:")
        print("=" * 50)

        iterator = SoundIterator(annotation_path)
        print(f"Всего файлов для итерации: {len(iterator)}")

        print("\nПервые 5 файлов:")
        for i, path in enumerate(iterator):
            if i < 5:
                print(f"{i + 1}: {os.path.basename(path)}")

        print("...")


if __name__ == "__main__":
    main()