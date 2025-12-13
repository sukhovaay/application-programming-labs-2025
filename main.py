import argparse
import sys
from pathlib import Path

from download import (
    FileIterator,
    write_csv_annotation,
    download_audio_from_fma
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Скачивание аудиофайлов на случайные темы с FMA. Вариант 17-30.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--audio-dir',
        type=str,
        required=True,
        help='Путь к папке для сохранения аудиофайлов (ОБЯЗАТЕЛЬНО).'
    )
    parser.add_argument(
        '--annotation',
        type=str,
        required=True,
        help='Путь к файлу аннотации в формате CSV (ОБЯЗАТЕЛЬНО).'
    )
    parser.add_argument(
        '--max-files',
        type=int,
        required=True,
        choices=range(50, 1001),
        help='Количество файлов для скачивания (ОБЯЗАТЕЛЬНО, от 50 до 1000).'
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Преобразуем аргументы в объекты Path
    audio_dir = Path(args.audio_dir)
    annotation_file = Path(args.annotation)

    print("=" * 50)
    print("ЗАПУСК ПРОГРАММЫ ДЛЯ ВАРИАНТА 17-30")
    print("=" * 50)
    print(f"Папка для аудио: {audio_dir}")
    print(f"Файл аннотации: {annotation_file}")
    print(f"Целевое количество файлов: {args.max_files}")
    print("=" * 50)

    # 1. Создаём папку для аудио
    audio_dir.mkdir(parents=True, exist_ok=True)

    # 2. Скачиваем аудиофайлы (функция вернёт пустой список, если FMA недоступен)
    print("\n[Этап 1] Попытка скачать аудиофайлы с Free Music Archive (FMA)...")
    downloaded_files = download_audio_from_fma(audio_dir, args.max_files)

    # 3. Если не удалось ничего скачать, создаём "заглушки" для демонстрации
    # Это позволит протестировать итератор и CSV даже без интернета.
    if not downloaded_files:
        print("\n[Предупреждение] Не удалось скачать файлы с FMA.")
        print("Создаю несколько тестовых файлов для демонстрации работы итератора и CSV.")
        for i in range(1, 6):
            dummy_file = audio_dir / f"demo_audio_{i:03d}.mp3"
            dummy_file.write_bytes(b'')  # Создаём пустой файл
            downloaded_files.append(dummy_file)
        print(f"Создано {len(downloaded_files)} тестовых файлов.")

    # 4. Создаём CSV-аннотацию для скачанных/созданных файлов
    print("\n[Этап 2] Создание CSV-аннотации...")
    write_csv_annotation(downloaded_files, annotation_file, audio_dir)

    # 5. Демонстрация работы итератора FileIterator
    print("\n[Этап 3] Демонстрация работы итератора FileIterator:")
    print("-" * 40)

    print("\n5а. Итерация по файлам из ПАПКИ (audio_dir):")
    dir_iterator = FileIterator(audio_dir)
    file_count_from_dir = 0
    for file_path in dir_iterator:
        if file_count_from_dir < 3:  # Покажем только первые 3
            print(f"   Найден файл: {file_path.name}")
        file_count_from_dir += 1
    print(f"   Всего файлов в папке: {file_count_from_dir}")

    print("\n5б. Итерация по файлам из CSV-АННОТАЦИИ:")
    csv_iterator = FileIterator(annotation_file)
    file_count_from_csv = 0
    for file_path in csv_iterator:
        if file_count_from_csv < 3:  # Покажем только первые 3
            print(f"   Прочитан путь из CSV: {file_path}")
        file_count_from_csv += 1
    print(f"   Всего путей прочитано из CSV: {file_count_from_csv}")

    print("\n" + "=" * 50)
    print("ВЫПОЛНЕНИЕ ЗАВЕРШЕНО")
    print("=" * 50)
    print(f"Итог: Обработано {len(downloaded_files)} аудиофайлов.")
    print(f"      Аннотация сохранена в '{annotation_file}'.")


if __name__ == "__main__":
    main()