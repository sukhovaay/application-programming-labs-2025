import os
import numpy as np
import matplotlib.pyplot as plt

def plot_audio_comparison(
    original_samples: np.ndarray,
    reversed_samples: np.ndarray,
    sampling_rate: int,
    input_filename: str,
    output_filename: str
) -> None:
    """
    Визуализация сравнения оригинального и перевернутого аудио.
    
    Создает графики амплитуды от времени для обоих аудиосигналов.
    """
    # Создание временной шкалы (в секундах)
    time_axis_original = np.arange(len(original_samples)) / sampling_rate
    time_axis_reversed = np.arange(len(reversed_samples)) / sampling_rate

    # Создание фигуры с двумя графиками
    figure, axes = plt.subplots(2, 1, figsize=(12, 10))

    # График 1: Оригинальное аудио
    if len(original_samples.shape) == 1:  # Моно
        axes[0].plot(time_axis_original, original_samples, color="blue", alpha=0.7, linewidth=0.5)
        axes[0].set_title(f"Оригинальное аудио (моно): {os.path.basename(input_filename)}")
    else:  # Стерео
        axes[0].plot(
            time_axis_original, original_samples[:, 0], 
            color="blue", alpha=0.7, linewidth=0.5, label="Левый канал"
        )
        axes[0].plot(
            time_axis_original, original_samples[:, 1], 
            color="red", alpha=0.7, linewidth=0.5, label="Правый канал"
        )
        axes[0].legend()
        axes[0].set_title(f"Оригинальное аудио (стерео): {os.path.basename(input_filename)}")

    axes[0].set_xlabel("Время (секунды)")
    axes[0].set_ylabel("Амплитуда")
    axes[0].axhline(0, color='black', linewidth=0.5, linestyle='--')
    axes[0].grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.7)

    # График 2: Перевернутое аудио
    if len(reversed_samples.shape) == 1:  # Моно
        axes[1].plot(time_axis_reversed, reversed_samples, color="green", alpha=0.7, linewidth=0.5)
        axes[1].set_title(f"Перевернутое аудио: {os.path.basename(output_filename)}")
    else:  # Стерео
        axes[1].plot(
            time_axis_reversed, reversed_samples[:, 0], 
            color="blue", alpha=0.7, linewidth=0.5, label="Левый канал"
        )
        axes[1].plot(
            time_axis_reversed, reversed_samples[:, 1], 
            color="red", alpha=0.7, linewidth=0.5, label="Правый канал"
        )
        axes[1].legend()
        axes[1].set_title(f"Перевернутое аудио: {os.path.basename(output_filename)}")

    axes[1].set_xlabel("Время (секунды)")
    axes[1].set_ylabel("Амплитуда")
    axes[1].axhline(0, color='black', linewidth=0.5, linestyle='--')
    axes[1].grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.7)

    plt.tight_layout()
    plt.show()