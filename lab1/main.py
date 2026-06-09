import os
import re
import string

# ---------- Шифр Цезаря ----------
def caesar_shift(char: str, key: int, encrypt: bool = True) -> str:
    """Сдвиг одного символа (только латинские буквы)."""
    if not char.isalpha() or char not in string.ascii_letters:
        return char
    base = ord('A') if char.isupper() else ord('a')
    offset = key if encrypt else -key
    return chr((ord(char) - base + offset) % 26 + base)

def caesar_encrypt(plaintext: str, key: int) -> str:
    return ''.join(caesar_shift(c, key, True) for c in plaintext)

def caesar_decrypt(ciphertext: str, key: int) -> str:
    return ''.join(caesar_shift(c, key, False) for c in ciphertext)

# ---------- Атака 1: известный открытый текст ----------
def known_plaintext_attack(plain: str, cipher: str):
    """Определить ключ по паре открытого и зашифрованного текстов."""
    # Ищем первую букву
    for p, c in zip(plain, cipher):
        if p.isalpha() and c.isalpha():
            p_base = ord('A') if p.isupper() else ord('a')
            c_base = ord('A') if c.isupper() else ord('a')
            # Вычисляем ключ: (c - p) mod 26
            key = (ord(c) - c_base - (ord(p) - p_base)) % 26
            # Проверяем весь текст на согласованность
            for pp, cc in zip(plain, cipher):
                if pp.isalpha() and cc.isalpha():
                    pp_shifted = caesar_shift(pp, key, True)
                    if pp_shifted != cc:
                        print("Ошибка: тексты не соответствуют одному ключу Цезаря.")
                        return None
            return key
    print("Не найдено ни одной буквы для определения ключа.")
    return None

# ---------- Атака 2: только шифрованный текст (перебор) ----------
def brute_force_all(ciphertext: str):
    """Вывод всех 26 вариантов расшифрования."""
    print("\nВсе возможные расшифровки:")
    for key in range(26):
        plain = caesar_decrypt(ciphertext, key)
        print(f"Ключ {key:2d}: {plain}")

# ---------- Атака 3: автоматический подбор по словарю ----------
# Встроенный список частых английских слов (будет использован при отсутствии файла)
FALLBACK_WORDS = {
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "i",
    "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
    "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
    "or", "an", "will", "my", "one", "all", "would", "there", "their", "what",
    "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
    "when", "make", "can", "like", "time", "no", "just", "him", "know", "take",
    "people", "into", "year", "your", "good", "some", "could", "them", "see", "other",
    "than", "then", "now", "look", "only", "come", "its", "over", "think", "also",
    "back", "after", "use", "two", "how", "our", "work", "first", "well", "way",
    "even", "new", "want", "because", "any", "these", "give", "day", "most", "us"
}

def load_dictionary(filepath="words.txt"):
    """Загрузка словаря из файла; если файла нет – fallback."""
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            words = {line.strip().lower() for line in f if line.strip()}
        print(f"Словарь загружен из файла: {len(words)} слов.")
        return words
    else:
        print(f"Файл '{filepath}' не найден. Использую встроенный словарь ({len(FALLBACK_WORDS)} слов).")
        return FALLBACK_WORDS.copy()

def score_decryption(text: str, dictionary: set) -> int:
    """Оценка расшифрованного текста: количество слов, найденных в словаре."""
    # Извлекаем слова (только буквы) и приводим к нижнему регистру
    words = re.findall(r'[a-zA-Z]+', text)
    words_lower = [w.lower() for w in words]
    return sum(1 for w in words_lower if w in dictionary)

def auto_crack(ciphertext: str, dictionary: set):
    """Автоматический подбор ключа, максимизирующий количество словарных слов."""
    best_keys = []
    best_score = -1
    results = []
    for key in range(26):
        plain = caesar_decrypt(ciphertext, key)
        sc = score_decryption(plain, dictionary)
        results.append((key, plain, sc))
        if sc > best_score:
            best_score = sc
            best_keys = [key]
        elif sc == best_score:
            best_keys.append(key)

    if best_score == 0:
        print("Ни один из вариантов не содержит известных слов. Возможно, текст не на английском или слишком короткий.")
        print("Вывод всех вариантов:")
        for key, plain, sc in results:
            print(f"Ключ {key:2d} (счёт {sc}): {plain}")
        return

    if len(best_keys) == 1:
        key = best_keys[0]
        print(f"Автоматически определён ключ: {key}")
        print(f"Расшифрованный текст: {results[key][1]}")
    else:
        print(f"Найдено несколько кандидатов с одинаковым максимальным счётом ({best_score}):")
        for key in best_keys:
            print(f"Ключ {key}: {results[key][1]}")

# ---------- Консольный интерфейс ----------
def main():
    dictionary = None  # ленивая загрузка

    while True:
        print("\n" + "="*50)
        print("ШИФР ЦЕЗАРЯ – МЕНЮ")
        print("1. Зашифровать текст")
        print("2. Расшифровать текст (с известным ключом)")
        print("3. Атака по известному открытому тексту")
        print("4. Атака только по шифрованному тексту (все ключи)")
        print("5. Автоматический взлом с помощью словаря")
        print("6. Выход")
        choice = input("Выберите пункт: ").strip()

        if choice == "1":
            text = input("Введите открытый текст: ")
            try:
                key = int(input("Введите ключ (0-25): "))
                if not 0 <= key <= 25:
                    raise ValueError
            except ValueError:
                print("Некорректный ключ.")
                continue
            print("Зашифрованный текст:", caesar_encrypt(text, key))

        elif choice == "2":
            text = input("Введите зашифрованный текст: ")
            try:
                key = int(input("Введите ключ (0-25): "))
                if not 0 <= key <= 25:
                    raise ValueError
            except ValueError:
                print("Некорректный ключ.")
                continue
            print("Расшифрованный текст:", caesar_decrypt(text, key))

        elif choice == "3":
            plain = input("Введите открытый текст: ")
            cipher = input("Введите соответствующий зашифрованный текст: ")
            key = known_plaintext_attack(plain, cipher)
            if key is not None:
                print(f"Определённый ключ: {key}")

        elif choice == "4":
            cipher = input("Введите зашифрованный текст: ")
            brute_force_all(cipher)

        elif choice == "5":
            if dictionary is None:
                dictionary = load_dictionary()
            cipher = input("Введите зашифрованный текст: ")
            auto_crack(cipher, dictionary)

        elif choice == "6":
            print("Выход.")
            break

        else:
            print("Неверный пункт. Попробуйте снова.")

if __name__ == "__main__":
    main()