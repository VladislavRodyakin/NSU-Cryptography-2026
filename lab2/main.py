"""
Вычисление информационной энтропии файла (по байтам).
Поддерживает режим генерации тестовых файлов.
"""

import sys
import math
import os
import random
from collections import Counter
from pathlib import Path


def count_byte_frequencies(filepath: str) -> Counter:
    """Подсчитывает частоты байтов в файле."""
    freq = Counter()
    try:
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                freq.update(chunk)
    except FileNotFoundError:
        print(f"Ошибка: файл '{filepath}' не найден.")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        sys.exit(1)
    return freq


def calculate_entropy(freq: Counter) -> float:
    """Вычисляет энтропию Шеннона по частотам байтов."""
    total = sum(freq.values())
    if total == 0:
        return 0.0

    entropy = 0.0
    for count in freq.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)
    return entropy


def print_frequencies(freq: Counter):
    """Выводит таблицу частот для встреченных байтов (0-255)."""
    if not freq:
        print("Файл пуст, частоты отсутствуют.")
        return

    total = sum(freq.values())
    print(f"{'Байт':>6} {'Символ':>6} {'Кол-во':>10} {'Вероятность':>15}")
    print("-" * 40)
    for byte in range(256):
        count = freq.get(byte, 0)
        if count > 0:
            p = count / total
            # Отображаем символ, если он печатный ASCII, иначе точку
            char = chr(byte) if 32 <= byte <= 126 else '.'
            print(f"{byte:6d} {char:>6} {count:10d} {p:15.6f}")
    print(f"\nВсего символов (байт): {total}")
    print(f"Размер алфавита (встреченные символы): {len(freq)}")


def compute_file_entropy(filepath: str):
    """Основная функция вычисления энтропии для заданного файла."""
    print(f"\nАнализ файла: {filepath}")
    freq = count_byte_frequencies(filepath)
    print_frequencies(freq)
    H = calculate_entropy(freq)
    print(f"Информационная энтропия: {H:.6f} бит/символ")
    alphabet = len(freq)
    if alphabet > 0:
        max_entropy = math.log2(alphabet) if alphabet > 1 else 0.0
        print(f"Максимально возможная энтропия для данного алфавита: {max_entropy:.6f} бит/символ")
    print()


def generate_test_files():
    """Создаёт тестовые файлы для проверки энтропии."""
    # Targets the folder containing this specific script
    script_dir = Path(__file__).resolve().parent
    test_dir = script_dir / "test_files"

    test_dir.mkdir(parents=True, exist_ok=True)

    # 1. Файл из одинаковых символов (например, символ 'A' = 65)
    same_char_path = os.path.join(test_dir, "same_char.bin")
    with open(same_char_path, 'wb') as f:
        f.write(b'A' * 100000)
    print(f"Создан файл: {same_char_path} (100 000 байт, все 'A')")

    # 2. Файл из случайных байтов 0 и 1 (алфавит размера 2)
    random_bits_path = os.path.join(test_dir, "random_bits.bin")
    with open(random_bits_path, 'wb') as f:
        data = bytes(random.randint(0, 1) for _ in range(100000))
        f.write(data)
    print(f"Создан файл: {random_bits_path} (100 000 случайных байтов 0/1)")

    # 3. Файл из случайных байтов 0-255
    random_bytes_path = os.path.join(test_dir, "random_bytes.bin")
    with open(random_bytes_path, 'wb') as f:
        data = bytes(random.randint(0, 255) for _ in range(100000))
        f.write(data)
    print(f"Создан файл: {random_bytes_path} (100 000 случайных байтов 0-255)")

    print("\nТестовые файлы готовы. Вы можете вычислить их энтропию с помощью этой программы.\n")


def main():
    print("=== Программа для вычисления информационной энтропии файла ===")
    while True:
        print("Меню:")
        print("1 - Вычислить энтропию файла")
        print("2 - Сгенерировать тестовые файлы")
        print("3 - Выход")
        choice = input("Ваш выбор: ").strip()

        if choice == '1':
            path = input("Введите путь к файлу: ").strip()
            if path:
                compute_file_entropy(path)
        elif choice == '2':
            generate_test_files()
        elif choice == '3':
            print("Завершение работы.")
            break
        else:
            print("Неверный ввод, попробуйте снова.\n")


if __name__ == "__main__":
    main()