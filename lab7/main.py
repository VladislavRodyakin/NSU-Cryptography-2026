import math

def mul(a, b, mod, counter):
    """Умножение по модулю с подсчётом."""
    counter[0] += 1
    return (a * b) % mod

def mod_pow(base, exp, mod, counter):
    """Быстрое возведение в степень с подсчётом умножений."""
    result = 1
    base = base % mod
    while exp > 0:
        if exp & 1:
            result = mul(result, base, mod, counter)
        base = mul(base, base, mod, counter)
        exp >>= 1
    return result

def mod_inv(a, p):
    """Обратный элемент по модулю p (через pow со степенью -1). Умножений нет."""
    return pow(a, -1, p)


def brute_force(g, h, p, counter):
    """Дискретный логарифм полным перебором. Возвращает x или None."""
    n = p - 1
    cur = 1
    for x in range(n):
        if cur == h:
            return x
        cur = mul(cur, g, p, counter)
    return None


def shanks(g, h, p, counter, verbose=True):
    """
    Метод Шэнкса с подробным выводом.
    Возвращает x или None.
    """
    n = p - 1                         # порядок группы Z_p*
    m = math.ceil(math.sqrt(n))       # размер «детских» шагов
    k = (n + m - 1) // m              # количество «великанских» шагов

    if verbose:
        print(f"\n=== Метод Шэнкса ===")
        print(f"Порядок группы n = {n}")
        print(f"Параметры: m = {m}, k = {k}")

    # Baby steps: g^j for j = 0 .. m-1
    baby = {}
    cur = 1
    baby[cur] = 0
    if verbose:
        print("\n--- Baby steps (сохраняем g^j) ---")
        print(f"j = 0 : {cur}")
    for j in range(1, m):
        cur = mul(cur, g, p, counter)
        if cur not in baby:
            baby[cur] = j
        if verbose:
            print(f"j = {j} : {cur}")


    gm = mod_pow(g, m, p, counter)
    inv_gm = mod_inv(gm, p)

    if verbose:
        print(f"\ng^{m} = {gm}")
        print(f"g^{{-m}} = {inv_gm}")

    # Giant steps: h * (g^{-m})^i для i = 0 .. k-1
    if verbose:
        print("\n--- Giant steps (ищем совпадение) ---")
    cur = h
    for i in range(k):
        if verbose:
            print(f"i = {i} : cur = {cur}", end="")
        if cur in baby:
            j = baby[cur]
            x = i * m + j
            if x < n:
                if verbose:
                    print(f"  -> СОВПАДЕНИЕ с j = {j}  => x = {i}*{m} + {j} = {x}")
                return x
        else:
            if verbose:
                print("  -> нет в таблице")
        if i < k - 1:
            cur = mul(cur, inv_gm, p, counter)
    return None


def compare_methods():
    """
    Запускает оба метода на нескольких тестовых примерах
    и выводит сравнительную таблицу.
    """
    examples = [
        # p, g, h
        (23, 5, 8),
        (29, 2, 3),
        (101, 2, 14),
        (1009, 11, pow(11, 15, 1009)),   # h = 11^15 mod 1009
    ]
    print("\n" + "=" * 70)
    print("Сравнение методов полного перебора и Шэнкса")
    print("=" * 70)
    print(f"{'p':<6} {'g':<4} {'h':<6} {'x (перебор)':<12} {'Умножений':<12} {'x (Шэнкс)':<12} {'Умножений':<12}")
    print("-" * 70)
    for p, g, h in examples:
        cnt_brute = [0]
        cnt_shanks = [0]

        x_brute = brute_force(g, h, p, cnt_brute)
        x_shanks = shanks(g, h, p, cnt_shanks, verbose=False)

        xb_str = str(x_brute) if x_brute is not None else "—"
        xs_str = str(x_shanks) if x_shanks is not None else "—"
        print(f"{p:<6} {g:<4} {h:<6} {xb_str:<12} {cnt_brute[0]:<12} {xs_str:<12} {cnt_shanks[0]:<12}")
    print("-" * 70)


def main():
    while True:
        print("\n" + "=" * 50)
        print("Дискретное логарифмирование")
        print("1. Ввести параметры и решить")
        print("2. Сравнение методов на примерах")
        print("3. Выход")
        choice = input("Ваш выбор: ").strip()

        if choice == "1":
            try:
                p = int(input("Введите простое число p: "))
                g = int(input("Введите основание g: "))
                h = int(input("Введите элемент h: "))
                if not (1 < g < p and 1 <= h < p):
                    print("Некорректные данные. Должно быть: 1 < g < p, 1 <= h < p.")
                    continue
            except ValueError:
                print("Ошибка ввода. Введите целые числа.")
                continue

            cnt_brute = [0]
            cnt_shanks = [0]


            print("\n--- Метод полного перебора ---")
            x_brute = brute_force(g, h, p, cnt_brute)
            if x_brute is not None:
                print(f"Найден x = {x_brute}")
            else:
                print("Решение не найдено (h не принадлежит подгруппе g).")
            print(f"Количество умножений: {cnt_brute[0]}")


            x_shanks = shanks(g, h, p, cnt_shanks, verbose=True)
            if x_shanks is not None:
                print(f"\nРезультат (Шэнкс): x = {x_shanks}")
            else:
                print("\nРешение методом Шэнкса не найдено.")
            print(f"Количество умножений: {cnt_shanks[0]}")

            if x_brute is not None and x_shanks is not None:
                if x_brute == x_shanks:
                    print("\nОба метода дали одинаковый результат.")
                else:
                    print("\nВнимание: результаты различаются! Проверьте входные данные.")

        elif choice == "2":
            compare_methods()

        elif choice == "3":
            print("Выход.")
            break
        else:
            print("Неверный пункт меню. Попробуйте снова.")

if __name__ == "__main__":
    main()

