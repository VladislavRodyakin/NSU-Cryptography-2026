import os
import argparse
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


SALT_SIZE = 16          # размер соли в байтах
KEY_SIZE = 32           # 256 бит для AES-256
IV_SIZE = 16            # размер вектора инициализации
PBKDF2_ITERATIONS = 100_000   # количество итераций PBKDF2


def derive_key(password: str, salt: bytes) -> bytes:
    """Получение 256-битного ключа из пароля и соли."""
    return PBKDF2(password, salt, dkLen=KEY_SIZE, count=PBKDF2_ITERATIONS)


def encrypt_file(input_path: str, output_path: str, password: str):
    """Зашифрование файла."""
    # Генерация случайной соли и IV
    salt = get_random_bytes(SALT_SIZE)
    iv = get_random_bytes(IV_SIZE)
    key = derive_key(password, salt)

    cipher = AES.new(key, AES.MODE_CBC, iv)

    with open(input_path, 'rb') as f_in:
        plaintext = f_in.read()

    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))

    # Запись: соль + IV + шифртекст
    with open(output_path, 'wb') as f_out:
        f_out.write(salt + iv + ciphertext)

    print(f"Файл '{input_path}' успешно зашифрован в '{output_path}'.")


def decrypt_file(input_path: str, output_path: str, password: str):
    """Расшифрование файла."""
    with open(input_path, 'rb') as f_in:
        data = f_in.read()

    # Извлечение соли, IV и шифртекста
    if len(data) < SALT_SIZE + IV_SIZE + AES.block_size:
        raise ValueError("Файл повреждён или не является зашифрованным.")

    salt = data[:SALT_SIZE]
    iv = data[SALT_SIZE:SALT_SIZE + IV_SIZE]
    ciphertext = data[SALT_SIZE + IV_SIZE:]

    key = derive_key(password, salt)
    cipher = AES.new(key, AES.MODE_CBC, iv)

    try:
        plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    except (ValueError, KeyError) as e:
        raise ValueError("Невозможно расшифровать: неверный пароль или файл повреждён.") from e

    with open(output_path, 'wb') as f_out:
        f_out.write(plaintext)

    print(f"Файл '{input_path}' успешно расшифрован в '{output_path}'.")


def main():
    parser = argparse.ArgumentParser(
        description="Шифрование и расшифрование файлов с помощью AES-256-CBC (итеративный блочный шифр)."
    )
    subparsers = parser.add_subparsers(dest='command', required=True, help='Действие: encrypt или decrypt')

    # Подкоманда encrypt
    encrypt_parser = subparsers.add_parser('encrypt', help='Зашифровать файл')
    encrypt_parser.add_argument('input', help='Путь к исходному файлу')
    encrypt_parser.add_argument('output', help='Путь для сохранения зашифрованного файла')
    encrypt_parser.add_argument('--password', '-p', help='Пароль (если не указан, будет запрошен)')

    # Подкоманда decrypt
    decrypt_parser = subparsers.add_parser('decrypt', help='Расшифровать файл')
    decrypt_parser.add_argument('input', help='Путь к зашифрованному файлу')
    decrypt_parser.add_argument('output', help='Путь для сохранения расшифрованного файла')
    decrypt_parser.add_argument('--password', '-p', help='Пароль (если не указан, будет запрошен)')

    args = parser.parse_args()

    # Получение пароля
    password = args.password
    if not password:
        import getpass
        password = getpass.getpass("Введите пароль: ")

    try:
        if args.command == 'encrypt':
            encrypt_file(args.input, args.output, password)
        elif args.command == 'decrypt':
            decrypt_file(args.input, args.output, password)
    except Exception as e:
        print(f"Ошибка: {e}")
        exit(1)


if __name__ == '__main__':
    main()
