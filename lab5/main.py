import hashlib
import secrets
from typing import Dict, Tuple

def crypto_hash(data: str) -> str:
    """Возвращает SHA-256 хеш от строки data в виде hex-строки."""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def generate_hash_chain(seed: str, length: int) -> Tuple[list, str, int]:
    """
    Генерирует цепочку хешей длины length (S0, S1, ..., S_length).
    S0 = seed, S_{i} = H(S_{i-1}).
    Возвращает:
        - полный список [S0, S1, ..., S_length] (для пользователя),
        - последний элемент S_length (сохраняется на сервере),
        - количество оставшихся входов (length).
    """
    chain = [seed]
    for _ in range(length):
        chain.append(crypto_hash(chain[-1]))
    return chain, chain[-1], length

users_db: Dict[str, dict] = {}

def register_user(username: str, chain_length: int = 5) -> None:
    """Регистрирует нового пользователя, генерируя цепочку длины chain_length."""
    if username in users_db:
        print(f"Пользователь '{username}' уже существует.")
        return

    seed = secrets.token_hex(16)
    chain, last_hash, remaining = generate_hash_chain(seed, chain_length)

    users_db[username] = {
        'stored_hash': last_hash,
        'remaining': remaining
    }

    print(f"\nПользователь '{username}' зарегистрирован.")
    print(f"Длина цепочки: {chain_length}")
    print("Ваша секретная цепочка (сохраните её! Используйте элементы в обратном порядке):")
    for i, h in enumerate(chain):
        print(f"  S{i}: {h}")
    print("Первый вход: введите S{chain_length-1}, затем S{chain_length-2} и т.д.\n")

def login_user(username: str, presented_hash: str) -> bool:
    """
    Проверяет попытку входа.
    presented_hash – элемент цепочки, который вводит пользователь.
    Возвращает True при успехе, иначе False.
    """
    if username not in users_db:
        print(f"Пользователь '{username}' не найден.")
        return False

    record = users_db[username]
    if record['remaining'] == 0:
        print("Цепочка исчерпана. Пройдите повторную регистрацию.")
        return False

    if crypto_hash(presented_hash) != record['stored_hash']:
        print("Неверный код. Попытка входа отклонена.")
        return False

    record['stored_hash'] = presented_hash
    record['remaining'] -= 1
    print(f"Вход выполнен. Осталось попыток: {record['remaining']}")
    if record['remaining'] == 0:
        print("Цепочка полностью использована. Зарегистрируйтесь заново для продолжения.")
    return True


def main():
    while True:
        print("\n=== Система аутентификации на цепочке хешей ===")
        print("1. Регистрация")
        print("2. Вход")
        print("3. Выход")
        choice = input("Выберите действие: ").strip()

        if choice == '1':
            username = input("Введите имя пользователя: ").strip()
            if not username:
                print("Имя не может быть пустым.")
                continue
            try:
                length = int(input("Длина цепочки (по умолчанию 5): ").strip() or 5)
                if length < 1:
                    raise ValueError
            except ValueError:
                print("Некорректная длина, используется 5.")
                length = 5
            register_user(username, length)

        elif choice == '2':
            username = input("Введите имя пользователя: ").strip()
            presented = input("Введите очередной код из вашей цепочки: ").strip()
            login_user(username, presented)

        elif choice == '3':
            print("Завершение работы.")
            break
        else:
            print("Неизвестная команда. Попробуйте снова.")

if __name__ == "__main__":
    main()

