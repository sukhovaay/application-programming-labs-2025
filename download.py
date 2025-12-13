import csv
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup


class FileIterator:
    def __init__(self, source: Path) -> None:
        if not isinstance(source, Path):
            raise TypeError("Source must be a Path object")

        self.source = source
        self.file_paths: list[Path] = []
        self._index = 0

        if self.source.is_file() and self.source.suffix == ".csv":
            self._load_from_csv()
        elif self.source.is_dir():
            self._load_from_dir()
        else:
            raise ValueError(f"Source must be a directory or a .csv file. Got: {self.source}")

    def _load_from_csv(self) -> None:
        with self.source.open('r', encoding='utf-8', newline='') as file:
            reader = csv.DictReader(file)
            # Проверяем наличие колонки с абсолютным путём
            if 'absolute_path' in reader.fieldnames:
                for row in reader:
                    self.file_paths.append(Path(row['absolute_path']).resolve())
            else:
                raise KeyError("CSV файл должен содержать колонку 'absolute_path'.")
        print(f"[FileIterator] Загружено {len(self.file_paths)} путей из CSV: {self.source}")

    def _load_from_dir(self) -> None:
        for p in self.source.rglob("*.mp3"):
            if p.is_file():
                self.file_paths.append(p.resolve())
        print(f"[FileIterator] Найдено {len(self.file_paths)} .mp3 файлов в директории: {self.source}")

    def __iter__(self) -> "FileIterator":
        self._index = 0
        return self

    def __next__(self) -> Path:
        if self._index >= len(self.file_paths):
            raise StopIteration
        result = self.file_paths[self._index]
        self._index += 1
        return result


def download_audio_from_fma(out_dir: Path, max_files: int = 50) -> list[Path]:
    BASE_URL = "http://fma.demo.clever-age.com"
    # Случайные темы (папки) на FMA для разнообразия
    themes = ["rock", "pop", "electronic", "hip-hop", "jazz", "classical", "folk"]
    import random
    selected_theme = random.choice(themes)
    target_url = f"{BASE_URL}/explore/genre/{selected_theme}/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    print(f"[Скачивание] Используем тему: '{selected_theme}'")
    print(f"[Скачивание] URL: {target_url}")

    try:
        # Теория: requests.get()
        response = requests.get(target_url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[Скачивание] Ошибка при загрузке страницы: {e}")
        # Возвращаем пустой список, если сайт недоступен
        return []

    # Теория: BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")
    downloaded_files = []

    # Ищем все ссылки на страницы отдельных треков
    track_links = []
    for link in soup.find_all("a", href=True):
        href = link['href']
        # FIXME: Этот паттерн может потребовать корректировки под реальную структуру FMA
        if "/track/" in href and href not in track_links:
            full_url = BASE_URL + href if href.startswith("/") else href
            track_links.append(full_url)

    print(f"[Скачивание] Найдено {len(track_links)} ссылок на треки.")

    for i, track_page_url in enumerate(track_links):
        if len(downloaded_files) >= max_files:
            break

        try:
            time.sleep(0.5)  # Вежливая пауза
            track_resp = requests.get(track_page_url, headers=headers, timeout=15)
            track_soup = BeautifulSoup(track_resp.text, "html.parser")

            # Пытаемся найти прямую ссылку на MP3 файл
            audio_link = None
            # Вариант 1: Ищем тег <audio>
            audio_tag = track_soup.find("audio")
            if audio_tag and audio_tag.get("src"):
                audio_link = audio_tag["src"]
            # Вариант 2: Ищем ссылку с расширением .mp3
            if not audio_link:
                for a_tag in track_soup.find_all("a", href=True):
                    if a_tag['href'].endswith(".mp3"):
                        audio_link = a_tag['href']
                        break

            if audio_link:
                # Делаем ссылку абсолютной
                if audio_link.startswith("/"):
                    audio_link = BASE_URL + audio_link
                elif not audio_link.startswith("http"):
                    audio_link = BASE_URL + "/" + audio_link

                # Создаём имя файла
                filename = f"fma_{selected_theme}_{i+1:03d}.mp3"
                file_path = out_dir / filename

                # Скачиваем файл
                print(f"[Скачивание] ({len(downloaded_files)+1}/{max_files}) Загружаю: {filename}")
                audio_resp = requests.get(audio_link, headers=headers, stream=True, timeout=30)
                if audio_resp.status_code == 200:
                    with file_path.open("wb") as f:
                        for chunk in audio_resp.iter_content(chunk_size=8192):
                            f.write(chunk)
                    # Проверяем размер файла (косвенная проверка на длительность >10с)
                    if file_path.stat().st_size > 300 * 1024:  # Эмпирическое условие: >300KB
                        downloaded_files.append(file_path)
                    else:
                        print(f"[Скачивание] Файл слишком мал, возможно <10с. Удаляю.")
                        file_path.unlink(missing_ok=True)
        except Exception as e:
            print(f"[Скачивание] Пропуск трека из-за ошибки: {e}")
            continue

    print(f"[Скачивание] Готово. Успешно скачано файлов: {len(downloaded_files)}")
    return downloaded_files


def write_csv_annotation(files: list[Path], csv_path: Path, base_dir: Path) -> None:
    # Создаём директорию для CSV, если её нет
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    with csv_path.open("w", encoding="utf-8", newline="") as f:
        # Теория: создание writer объекта
        writer = csv.writer(f)
        # Записываем заголовки согласно заданию (абсолютный и относительный путь)
        writer.writerow(["absolute_path", "relative_path"])
        for p in files:
            abs_p = p.resolve()
            try:
                # Пытаемся вычислить относительный путь относительно base_dir
                rel_p = abs_p.relative_to(base_dir.resolve())
            except ValueError:
                # Если файл не находится внутри base_dir, используем только имя
                rel_p = Path(p.name)
            # Теория: запись строки
            writer.writerow([str(abs_p), str(rel_p)])
    print(f"[Аннотация] CSV файл создан: {csv_path}")