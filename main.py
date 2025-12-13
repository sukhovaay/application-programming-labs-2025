from arg import parse_command_line_args
from audio import read_audio_file, reverse_audio_samples, save_audio_samples
from vis import plot_audio_comparison

def main():
    print("=" * 60)
    print("ОБРАБОТКА АУДИОФАЙЛОВ: ПЕРЕВОРАЧИВАНИЕ АУДИО")
    print("=" * 60)
    
    try:
        # 1. Парсинг аргументов командной строки
        args = parse_command_line_args()
        
        print(f"\nВходной файл: {args.input_file_path}")
        print(f"Выходной файл: {args.output_file_path}")

        # 2. Загрузка аудиофайла
        print("\n[1/4] ЗАГРУЗКА АУДИОФАЙЛА")
        try:
            audio_samples, sample_rate, channels_count = read_audio_file(args.input_file_path)
        except Exception as error:
            raise Exception(f"Ошибка при чтении файла: {error}")

        # 3. Обработка аудио
        print("\n[2/4] ОБРАБОТКА АУДИО (ПЕРЕВОРАЧИВАНИЕ)")
        try:
            reversed_audio_samples = reverse_audio_samples(audio_samples)
        except Exception as error:
            raise Exception(f"Ошибка при переворачивании аудио: {error}")

        # 4. Визуализация
        print("\n[3/4] ВИЗУАЛИЗАЦИЯ РЕЗУЛЬТАТОВ")
        try:
            plot_audio_comparison(
                audio_samples, 
                reversed_audio_samples, 
                sample_rate,
                args.input_file_path,
                args.output_file_path
            )
        except ImportError:
            print("Matplotlib не установлен. Пропускаем визуализацию.")
        except Exception as error:
            print(f"Ошибка при визуализации: {error}")
            print("Продолжаем выполнение...")

        # 5. Сохранение результата
        print("\n[4/4] СОХРАНЕНИЕ РЕЗУЛЬТАТА")
        try:
            save_audio_samples(reversed_audio_samples, sample_rate, args.output_file_path)
        except Exception as error:
            raise Exception(f"Ошибка при сохранении файла: {error}")

        # Итоговое сообщение
        print("\n" + "=" * 60)
        print("ОБРАБОТКА УСПЕШНО ЗАВЕРШЕНА!")
        print(f"Обработано сэмплов: {len(audio_samples)}")
        print(f"Длительность аудио: {len(audio_samples) / sample_rate:.2f} сек")
        print("=" * 60)

    except SystemExit:
        # Выход при ошибках аргументов
        pass
    except KeyboardInterrupt:
        print("\n\nВыполнение прервано пользователем.")
    except Exception as error:
        print(f"\nКРИТИЧЕСКАЯ ОШИБКА: {error}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())