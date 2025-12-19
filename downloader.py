"""
Модуль для скачивания звуковых файлов с mixkit.co.
"""

import csv
import os
import time
import random
import re
import requests
from bs4 import BeautifulSoup


class SoundDownloader:
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        self.base_url = "https://mixkit.co"

    def get_sound_pages(self) -> list:
        sound_pages = []
        sections = [
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

        for section in sections:
            if len(sound_pages) >= 100:
                break

            url = self.base_url + section
            print(f"Поиск в разделе: {section}")

            try:
                response = self.session.get(url)
                soup = BeautifulSoup(response.text, "html.parser")
                all_links = soup.find_all("a", href=True)

                for link in all_links:
                    href = link["href"]
                    if href.startswith("/free-sound-effects/") and href.count("/") == 3:
                        full_url = self.base_url + href
                        if full_url not in sound_pages:
                            sound_pages.append(full_url)

                time.sleep(1)

            except Exception as e:
                raise Exception(f"Ошибка при парсинге раздела {section}: {e}")

        return sound_pages

    def parse_duration(self, duration_str: str) -> int:
        if not duration_str:
            return 0

        duration_str = duration_str.strip()
        duration_str = re.sub(r"\s+", "", duration_str)

        if ":" in duration_str:
            parts = duration_str.split(":")
            if len(parts) == 2:
                try:
                    minutes = int(parts[0])
                    seconds = int(parts[1])
                    return minutes * 60 + seconds
                except ValueError:
                    return 0

        numbers = re.findall(r"\d+", duration_str)
        if numbers:
            if len(numbers) == 1:
                return int(numbers[0])
            elif len(numbers) == 2:
                return int(numbers[0]) * 60 + int(numbers[1])

        return 0

    def get_duration_and_audio_url(self, page_url: str) -> tuple:
        try:
            response = self.session.get(page_url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            duration_elem = soup.find("div", class_="item-grid-sfx-preview__meta-time")
            if not duration_elem:
                duration_elem = soup.find("div", {"data-test-id": "duration"})

            duration_sec = 0
            if duration_elem:
                duration_text = duration_elem.get_text(strip=True)
                duration_sec = self.parse_duration(duration_text)
                print(f"Найдена длительность: {duration_text} -> {duration_sec} сек")

            audio_div = soup.find("div", {"data-audio-player-preview-url-value": True})
            audio_url = None
            if audio_div:
                audio_url = audio_div.get("data-audio-player-preview-url-value")

            return duration_sec, audio_url

        except Exception as e:
            print(f"Ошибка извлечения данных со страницы {page_url}: {e}")
            return 0, None

    def download_sound_from_page(self, page_url: str, download_folder: str, 
                                 min_duration: int = 10) -> tuple:
        duration_sec, audio_url = self.get_duration_and_audio_url(page_url)

        if duration_sec <= min_duration:
            print(f"Пропущен (слишком короткий: {duration_sec} сек): {page_url}")
            return None, None

        if not audio_url or not audio_url.startswith("http"):
            print(f"Некорректный аудио URL: {audio_url}")
            return None, None

        filename = os.path.basename(audio_url)
        if not filename.endswith(".mp3"):
            filename += ".mp3"
        filepath = os.path.join(download_folder, filename)

        print(f"Скачивание ({duration_sec} сек): {filename}")
        try:
            audio_response = self.session.get(audio_url, timeout=30)
            if audio_response.status_code == 200:
                with open(filepath, "wb") as f:
                    f.write(audio_response.content)

                if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                    return filepath, filename
                else:
                    print(f"Файл не скачался или пустой: {filename}")
                    return None, None
            else:
                print(f"Ошибка HTTP {audio_response.status_code}: {audio_url}")
        except Exception as e:
            print(f"Ошибка скачивания {filename}: {e}")

        return None, None

    def download_sounds(self, download_folder: str, min_files: int = 50, 
                       max_files: int = 1000, min_duration: int = 10) -> str:
        os.makedirs(download_folder, exist_ok=True)
        annotation_file = os.path.join(download_folder, "annotation.csv")

        print("Поиск страниц со звуками...")
        sound_pages = self.get_sound_pages()
        print(f"Найдено потенциальных звуков: {len(sound_pages)}")

        with open(annotation_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                ["absolute_path", "relative_path", "filename", "duration_seconds"]
            )

            downloaded = 0
            for i, page_url in enumerate(sound_pages):
                if downloaded >= max_files:
                    break

                print(f"\n--- Обработка {i + 1}/{len(sound_pages)} ---")
                filepath, filename = self.download_sound_from_page(
                    page_url, download_folder, min_duration
                )

                if filepath and os.path.exists(filepath):
                    absolute_path = os.path.abspath(filepath)
                    relative_path = os.path.relpath(filepath, download_folder)
                    duration_sec, _ = self.get_duration_and_audio_url(page_url)

                    writer.writerow(
                        [absolute_path, relative_path, filename, duration_sec]
                    )
                    downloaded += 1
                    print(
                        f"Сохранён: {filename} ({duration_sec} сек) [{downloaded}/{max_files}]"
                    )
                else:
                    print("Пропущен или ошибка загрузки")

                time.sleep(random.uniform(1, 2))

        print(f"\nЗавершено! Скачано файлов: {downloaded}")
        if downloaded < min_files:
            print(f"Внимание: скачано меньше минимального количества ({min_files})")

        return annotation_file