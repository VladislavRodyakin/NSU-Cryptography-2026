import random
import time

def generate_lcg_bytes(size: int, seed: int = None) -> bytes:
    """
    Линейный конгруэнтный генератор (LCG) с параметрами из glibc.
    Возвращает size псевдослучайных байт.
    """
    if seed is None:
        seed = int(time.time() * 1000) % (2**31)
        m = 2**31
        a = 1103515245
        c = 12345
        state = seed & 0x7fffffff  # 31 бит
        result = bytearray()
        for _ in range(size):
            state = (a * state + c) % m
            # Берём старший байт состояния (наиболее случайный)
            result.append((state >> 23) & 0xFF)
        
        return bytes(result)

def generate_rand_bytes_builtin(size: int) -> bytes:
    """Генерация случайных байт с помощью встроенного ГПСЧ (random.randbytes)."""
    return random.randbytes(size)

def read_file_bytes(filename: str) -> bytes:
    with open(filename, 'rb') as f:
        return f.read()

def write_file_bytes(filename: str, data: bytes):
    with open(filename, 'wb') as f:
        f.write(data)


def vernam_crypt(input_file: str, key_file: str, output_file: str):
    """
    Зашифрование / расшифрование шифром Вернама.
    Операция XOR над байтами открытого текста и ключа.
    Ключ должен быть не короче входного файла.
    """
    plaintext = read_file_bytes(input_file)
    key = read_file_bytes(key_file)
    if len(key) < len(plaintext):
        raise ValueError(f"Длина ключа ({len(key)} байт) меньше длины файла ({len(plaintext)} байт). "
                         "Сгенерируйте ключ подходящего размера.")
# XOR только по длине открытого текста
    ciphertext = bytes(p ^ key[i] for i, p in enumerate(plaintext))
    write_file_bytes(output_file, ciphertext)
    print(f"Операция выполнена. Результат сохранён в {output_file}")


def rc4_ksa(key: bytes) -> list:
    """Алгоритм планирования ключа (Key Scheduling Algorithm) RC4."""
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]
    return S

def rc4_prga(S: list, length: int) -> bytes:
    """Генерация псевдослучайной гаммы (PRGA) заданной длины."""
    i = j = 0
    keystream = bytearray()
    S = S[:]  # копируем, чтобы не изменять исходное состояние
    for _ in range(length):
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        K = S[(S[i] + S[j]) % 256]
        keystream.append(K)
    return bytes(keystream)

def rc4_crypt(input_file: str, key_str: str, output_file: str):
        """
        Зашифрование / расшифрование поточным шифром RC4.
        Ключ задаётся строкой (преобразуется в байты в кодировке UTF-8).
        """
        key = key_str.encode('utf-8')
        plaintext = read_file_bytes(input_file)
        S = rc4_ksa(key)
        keystream = rc4_prga(S, len(plaintext))
        ciphertext = bytes(p ^ k for p, k in zip(plaintext, keystream))
        write_file_bytes(output_file, ciphertext)
        print(f"Операция выполнена. Результат сохранён в {output_file}")


def menu():
    print("\n=== ПОТОЧНЫЕ ШИФРЫ ===")
    print("1. Сгенерировать файл-ключ для шифра Вернама")
    print("2. Зашифровать файл (Вернам)")
    print("3. Расшифровать файл (Вернам)")
    print("4. Зашифровать/расшифровать файл (RC4)")
    print("0. Выход")
    return input("Выберите действие: ").strip()

def main():
    while True:
        choice = menu()
        if choice == '1':
            try:
                size = int(input("Размер ключа (в байтах): "))
                if size <= 0:
                    print("Размер должен быть положительным.")
                    continue
                print("Метод генерации:")
                print("  1 - встроенный ГПСЧ (random.randbytes)")
                print("  2 - линейный конгруэнтный генератор (LCG)")
                method = input("Выберите метод (1/2): ").strip()
                seed_str = input("Seed для LCG (Enter для автоматического): ").strip()
                seed = int(seed_str) if seed_str else None
                filename = input("Имя выходного файла: ").strip()
                if method == '1':
                    data = generate_rand_bytes_builtin(size)
                elif method == '2':
                    data = generate_lcg_bytes(size, seed)
                else:
                    print("Неверный метод.")
                    continue
                write_file_bytes(filename, data)
                print(f"Файл-ключ {filename} успешно создан ({size} байт).")
            except ValueError as e:
                print(f"Ошибка: {e}")
            except Exception as e:
                print(f"Ошибка: {e}")
        
        elif choice == '2':
            try:
                input_file = input("Файл с открытым текстом: ").strip()
                key_file = input("Файл с ключом (из п.1): ").strip()
                output_file = input("Выходной файл (шифртекст): ").strip()
                vernam_crypt(input_file, key_file, output_file)
            except FileNotFoundError as e:
                print(f"Файл не найден: {e}")
            except ValueError as e:
                print(f"Ошибка: {e}")
        
        elif choice == '3':
            try:
                input_file = input("Файл с шифртекстом: ").strip()
                key_file = input("Файл с ключом: ").strip()
                output_file = input("Выходной файл (открытый текст): ").strip()
                vernam_crypt(input_file, key_file, output_file)
            except FileNotFoundError as e:
                print(f"Файл не найден: {e}")
            except ValueError as e:
                print(f"Ошибка: {e}")
        
        elif choice == '4':
            try:
                input_file = input("Входной файл: ").strip()
                key_str = input("Секретный ключ (строка): ").strip()
                output_file = input("Выходной файл: ").strip()
                rc4_crypt(input_file, key_str, output_file)
            except FileNotFoundError as e:
                print(f"Файл не найден: {e}")
            except Exception as e:
                print(f"Ошибка: {e}")
        
        elif choice == '0':
            print("Выход.")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    main()
