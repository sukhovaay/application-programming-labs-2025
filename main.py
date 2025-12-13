import argparse
import csv
import os
import random
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup


def handle_cli_args():
    """Обрабатывает и валидирует аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="Загрузчик аудиофайлов длительностью более 10 секунд с Mixkit"
    )
    parser.add_argument(
        "--target-dir",
        "-t",
        required=True,
        help="Целевая директория для сохранения аудиофайлов",
    )
    parser.add_argument(
        "--min-count", type=int, default=50, help="Минимальное требуемое количество файлов"
    )
    parser.add_argument(
        "--max-count", type=int, default=100, help="Максимальное количество файлов для загрузки"
    )
    args = parser.parse_args()

    if not (50 <= args.max_count <= 1000):
        parser.error("Аргумент --max-count должен быть в диапазоне от 50 до 1000")
    if args.min_count > args.max_count:
        parser.error("Аргумент --min-count не может превышать --max-count")

    return args


class AudioHarvester:
    """Основной класс для поиска и загрузки аудио."""

    def __init__(self):
        self.http_client = requests.Session()
        self.http_client.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        self.site_root = "https://mixkit.co"

    def discover_audio_pages(self):
        """Собирает URL страниц с аудиозаписями из различных категорий."""
        discovered_urls = []
        category_list = [
            "/free-sound-effects/",
            "/free-sound-effects/animals/",
            "/free-sound-effects/cartoon/",
            "/free-sound-effects/city/",
            "/free-sound-effects/nature/",
            "/free-sound-effects/people/",
            "/free-sound-effects/science-fiction/",
            "/free-sound-effects/sports/",
            "/free-sound-effects/technology/",
            "/free-sound-effects/transportation/",
        ]

        for category_path in category_list:
            if len(discovered_urls) >= 100:
                break
            full_url = self.site_root + category_path
            print(f"Сканирую категорию: {category_path}")

            try:
                page_response = self.http_client.get(full_url)
                page_soup = BeautifulSoup(page_response.text, "html.parser")
                all_page_links = page_soup.find_all("a", href=True)

                for link_tag in all_page_links:
                    href_value = link_tag["href"]
                    # Ищем ссылки на отдельные страницы звуков
                    if href_value.startswith("/free-sound-effects/") and href_value.count("/") == 3:
                        complete_url = self.site_root + href_value
                        if complete_url not in discovered_urls:
                            discovered_urls.append(complete_url)
                time.sleep(1)
            except Exception as err:
                print(f"Ошибка при обработке категории {category_path}: {err}")
                continue

        return discovered_urls

    def extract_duration_seconds(self, duration_text):
        """Конвертирует строковое представление длительности в секунды (int)."""
        if not duration_text:
            return 0
        clean_text = duration_text.strip().replace(" ", "")
        # Обрабатываем формат "минуты:секунды"
        if ":" in clean_text:
            parts = clean_text.split(":")
            if len(parts) == 2:
                try:
                    return int(parts[0]) * 60 + int(parts[1])
                except ValueError:
                    return 0
        # Пытаемся извлечь числа из текста
        numeric_parts = re.findall(r"\d+", clean_text)
        if len(numeric_parts) == 1:
            return int(numeric_parts[0])
        elif len(numeric_parts) == 2:
            return int(numeric_parts[0]) * 60 + int(numeric_parts[1])
        return 0

    def get_audio_metadata(self, page_url):
        """Получает длительность и прямую ссылку на аудиофайл со страницы."""
        try:
            page_response = self.http_client.get(page_url, timeout=10)
            page_soup = BeautifulSoup(page_response.text, "html.parser")

            # Поиск элемента с длительностью
            duration_element = page_soup.find("div", class_="item-grid-sfx-preview__meta-time")
            if not duration_element:
                duration_element = page_soup.find("div", {"data-test-id": "duration"})

            duration_seconds = 0
            if duration_element:
                raw_duration = duration_element.get_text(strip=True)
                duration_seconds = self.extract_duration_seconds(raw_duration)
                print(f"Длительность найдена: {raw_duration} -> {duration_seconds} сек")

            # Поиск элемента с ссылкой на аудио
            audio_data_div = page_soup.find("div", {"data-audio-player-preview-url-value": True})
            direct_audio_url = audio_data_div.get("data-audio-player-preview-url-value") if audio_data_div else None

            return duration_seconds, direct_audio_url

        except Exception as err:
            print(f"Ошибка получения данных со страницы {page_url}: {err}")
            return 0, None

    def fetch_audio_file(self, page_url, output_dir, duration_threshold=10):
        """Загружает аудиофайл, если его длительность превышает порог."""
        track_duration, audio_source_url = self.get_audio_metadata(page_url)
        if track_duration <= duration_threshold:
            print(f"Пропускаю (малая длительность {track_duration}с): {page_url}")
            return None, None
        if not audio_source_url:
            print(f"Не найдена ссылка на аудио: {page_url}")
            return None, None
        if not audio_source_url.startswith("http"):
            print(f"Ссылка имеет неверный формат: {audio_source_url}")
            return None, None

        # Формирование имени и пути для файла
        base_name = os.path.basename(audio_source_url)
        if not base_name.endswith(".mp3"):
            base_name += ".mp3"
        final_path = os.path.join(output_dir, base_name)

        print(f"Загрузка ({track_duration} сек): {base_name}")
        try:
            audio_response = self.http_client.get(audio_source_url, timeout=30)
            if audio_response.status_code == 200:
                with open(final_path, "wb") as audio_file:
                    audio_file.write(audio_response.content)
                # Проверка успешности сохранения
                if os.path.exists(final_path) and os.path.getsize(final_path) > 0:
                    return final_path, base_name
                else:
                    print(f"Файл не был сохранён или пуст: {base_name}")
                    return None, None
            else:
                print(f"Ошибка HTTP {audio_response.status_code} для {audio_source_url}")
        except Exception as err:
            print(f"Ошибка загрузки {base_name}: {err}")

        return None, None

    def execute_download(self, output_dir, min_files=50, max_files=1000, min_duration=10):
        """Основной метод, управляющий процессом загрузки."""
        os.makedirs(output_dir, exist_ok=True)
        meta_file_path = os.path.join(output_dir, "audio_metadata.csv")

        print("Поиск страниц с аудио...")
        page_list = self.discover_audio_pages()
        print(f"Найдено страниц для обработки: {len(page_list)}")

        with open(meta_file_path, "w", newline="", encoding="utf-8") as meta_file:
            csv_writer = csv.writer(meta_file)
            csv_writer.writerow(["absolute_path", "relative_path", "filename", "duration_seconds"])

            success_count = 0
            for idx, current_page in enumerate(page_list):
                if success_count >= max_files:
                    break

                print(f"\n--- Страница {idx + 1}/{len(page_list)} ---")
                saved_path, saved_name = self.fetch_audio_file(current_page, output_dir, min_duration)

                if saved_path and os.path.exists(saved_path):
                    abs_path = os.path.abspath(saved_path)
                    rel_path = os.path.relpath(saved_path, output_dir)
                    # Получаем длительность повторно для записи
                    actual_duration, _ = self.get_audio_metadata(current_page)
                    csv_writer.writerow([abs_path, rel_path, saved_name, actual_duration])
                    success_count += 1
                    print(f"Успешно: {saved_name} ({actual_duration} сек) [{success_count}/{max_files}]")
                else:
                    print("Файл не был загружен.")

                time.sleep(random.uniform(1, 2))

        print(f"\nГотово! Загружено файлов: {success_count}")
        if success_count < min_files:
            print(f"Внимание: загружено меньше требуемого минимума ({min_files})")

        return meta_file_path


class AudioCollection:
    """Итератор для работы с коллекцией аудиофайлов."""

    def __init__(self, source):
        """Инициализация итератора. Источником может быть CSV-файл или директория."""
        self.item_list = []
        if os.path.isfile(source):
            # Загрузка путей из CSV
            with open(source, "r", encoding="utf-8") as f:
                csv_reader = csv.reader(f)
                next(csv_reader, None)
                for row in csv_reader:
                    if row and len(row) > 0:
                        potential_path = row[0]
                        if os.path.exists(potential_path):
                            self.item_list.append(potential_path)
            print(f"Загружено {len(self.item_list)} записей из файла метаданных")
        elif os.path.isdir(source):
            # Сканирование директории
            for root_dir, _, files in os.walk(source):
                for file_name in files:
                    if file_name.lower().endswith((".mp3", ".wav", ".ogg")):
                        self.item_list.append(os.path.join(root_dir, file_name))
            print(f"Найдено {len(self.item_list)} файлов в директории")
        else:
            raise ValueError(f"Указанный источник не существует: {source}")

        self.current_position = 0

    def __iter__(self):
        self.current_position = 0
        return self

    def __next__(self):
        if self.current_position < len(self.item_list):
            next_item = self.item_list[self.current_position]
            self.current_position += 1
            return next_item
        raise StopIteration

    def __len__(self):
        return len(self.item_list)


def run_program():
    """Точка входа в программу."""
    cli_args = handle_cli_args()

    audio_fetcher = AudioHarvester()
    metadata_path = audio_fetcher.execute_download(
        output_dir=cli_args.target_dir,
        min_files=cli_args.min_count,
        max_files=cli_args.max_count,
        min_duration=10,
    )

    # Демонстрация работы итератора
    if metadata_path and os.path.exists(metadata_path):
        print("\n" + "=" * 50)
        print("Работа итератора по коллекции:")
        print("=" * 50)

        collection_iter = AudioCollection(metadata_path)
        print(f"Всего элементов для перебора: {len(collection_iter)}")

        print("\nПервые 5 элементов коллекции:")
        for i, elem_path in enumerate(collection_iter):
            if i < 5:
                print(f"{i + 1}: {os.path.basename(elem_path)}")
        print("...")


if __name__ == "__main__":
    run_program()