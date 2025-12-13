import os
import numpy as np
import soundfile as sf
from typing import Tuple

def read_audio_file(file_path: str) -> Tuple[np.ndarray, int, int]:
    """
    Чтение аудиофайла с выводом характеристик.
    
    Возвращает:
    - samples_array: массив сэмплов (амплитуд)
    - sampling_rate: частота дискретизации (Гц)
    - num_channels: количество каналов
    """
    try:
        # Чтение данных: samples_array содержит сэмплы, sampling_rate - частоту дискретизации
        samples_array, sampling_rate = sf.read(file_path)

        # Определяем количество каналов (моно/стерео)
        if len(samples_array.shape) == 1:
            num_channels = 1
            audio_type_info = f"Моно, {len(samples_array)} сэмплов"
        else:
            num_channels = samples_array.shape[1]
            audio_type_info = f"Стерео ({num_channels} канала), {len(samples_array)} сэмплов"

        # Вывод информации об аудиофайле
        print("=" * 50)
        print("ХАРАКТЕРИСТИКИ АУДИОФАЙЛА:")
        print(f"Тип аудио: {audio_type_info}")
        print(f"Частота дискретизации: {sampling_rate} Гц")
        print(f"Длительность: {len(samples_array) / sampling_rate:.2f} секунд")
        print(f"Тип данных массива: {samples_array.dtype}")
        print(f"Диапазон амплитуд: [{samples_array.min():.3f}, {samples_array.max():.3f}]")
        print("=" * 50)

        return samples_array, sampling_rate, num_channels

    except Exception as error:
        raise Exception(
            f"Ошибка при чтении файла: {error}\n"
            f"Убедитесь, что файл существует и имеет поддерживаемый формат."
        )

def reverse_audio_samples(samples_array: np.ndarray) -> np.ndarray:
    """
    Переворачивает аудио задом наперед путем инверсии порядка сэмплов.
    """
    print(f"Инвертирование порядка {len(samples_array)} сэмплов...")
    return np.flip(samples_array, axis=0)

def save_audio_samples(
    samples_array: np.ndarray, 
    sampling_rate: int, 
    output_path: str
) -> None:
    """
    Сохранение массива сэмплов в аудиофайл.
    """
    try:
        sf.write(output_path, samples_array, sampling_rate)
        print(f"Аудиофайл успешно сохранен: {output_path}")
        print(f"Размер файла: {os.path.getsize(output_path) / 1024:.2f} КБ")
    except Exception as error:
        raise Exception(f"Ошибка при сохранении файла: {error}")