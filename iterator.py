"""
Модуль для итерации по аудиофайлам.
"""

import csv
import os


class SoundIterator:
    
    def __init__(self, annotation_source: str):
        self.file_paths = []

        if os.path.isfile(annotation_source):
            self._load_from_csv(annotation_source)
        elif os.path.isdir(annotation_source):
            self._load_from_folder(annotation_source)
        else:
            raise ValueError(
                f"Укажите существующий CSV-файл или папку: {annotation_source}"
            )

    def _load_from_csv(self, csv_path: str) -> None:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)  # пропуск заголовка
            for row in reader:
                if row and len(row) > 0:
                    abs_path = row[0]
                    if os.path.exists(abs_path):
                        self.file_paths.append(abs_path)
        print(f"Загружено {len(self.file_paths)} путей из аннотации")

    def _load_from_folder(self, folder_path: str) -> None:
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith((".mp3", ".wav", ".ogg")):
                    self.file_paths.append(os.path.join(root, file))
        print(f"Загружено {len(self.file_paths)} файлов из папки")

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self) -> str:
        if self._index < len(self.file_paths):
            path = self.file_paths[self._index]
            self._index += 1
            return path
        else:
            raise StopIteration

    def __len__(self) -> int:
        return len(self.file_paths)