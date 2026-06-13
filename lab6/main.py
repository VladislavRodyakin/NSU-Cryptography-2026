import time

def hamming_weight(n):
    """Вес Хэмминга — количество единиц в двоичной записи числа."""
    return bin(n).count('1')

def fast_pow(base, exponent, mod=None, verbose=False):
    """
    Быстрое возведение в степень с модулем (опционально).
    Возвращает (результат, общее_количество_умножений).
    """
    if exponent == 0:
        return 1 % mod if mod else 1, 0

    result = 1
    current = base
    square_steps = 0
    mult_steps = 0
    step = 1  # номер шага для трассировки

    # Сохраняем исходные значения для вывода в шапке трассировки
    original_exp = exponent
    original_base = base

    if verbose:
        print("\n" + "="*80)
        print(f"Быстрое возведение в степень: {base}^{exponent}" + (f" mod {mod}" if mod else ""))
        print(f"Вес Хэмминга показателя: {hamming_weight(original_exp)}")
        print("="*80)
        print(f"{'Step':<6} {'exp (binary)':<20} {'current':<20} {'result':<20} {'Действие'}")
        print("-"*80)

    while exponent > 0:
        if verbose:
            # выводим состояние перед обработкой младшего бита
            bin_exp = bin(exponent)[2:]
            print(f"{step:<6} {bin_exp:<20} {current:<20} {result:<20} ", end="")

        # если младший бит = 1 → умножаем результат на current
        if exponent & 1:
            result = result * current
            mult_steps += 1
            if mod:
                result %= mod
            if verbose:
                print(f"умножить: result = result * current → {result}")
        else:
            if verbose:
                print(f"─")

        # возводим current в квадрат (всегда)
        current = current * current
        square_steps += 1
        if mod:
            current %= mod

        exponent //= 2
        step += 1

    total_mult = square_steps + mult_steps
    if verbose:
        print("-"*80)
        print(f"Всего умножений (возведение в квадрат + умножения): {total_mult}")
        print(f"  - возведений в квадрат: {square_steps}")
        print(f"  - умножений результата: {mult_steps}")
        print(f"Результат: {result}")
        print("="*80 + "\n")

    return result, total_mult

def simple_pow(a, b, m=None):
    """Наивное возведение в степень для проверки (только с целым показателем)."""
    if b == 0:
        return 1 % m if m else 1
    res = 1
    for _ in range(b):
        res *= a
        if m:
            res %= m
    return res

def main():
    print("Реализация быстрого возведения в степень с трассировкой.")
    print("Допускается работа с модулем (опционально).")

    while True:
        try:
            base_str = input("Введите основание (целое число): ").strip()
            base = int(base_str)

            exp_str = input("Введите показатель (целое неотрицательное число): ").strip()
            exponent = int(exp_str)
            if exponent < 0:
                print("Показатель должен быть неотрицательным. Попробуйте снова.\n")
                continue

            mod_str = input("Введите модуль (целое положительное число) или оставьте пустым: ").strip()
            mod = int(mod_str) if mod_str else None
            if mod is not None and mod <= 0:
                print("Модуль должен быть положительным. Попробуйте снова.\n")
                continue

            start = time.perf_counter()
            res_fast, steps_fast = fast_pow(base, exponent, mod, verbose=True)
            end = time.perf_counter()
            print(f"⏱ Время выполнения быстрого алгоритма: {end - start:.6f} сек")
            print(f"Количество умножений (всего): {steps_fast}")
            print(f"Вес Хэмминга показателя: {hamming_weight(exponent)}\n")

            # check simple only for small exponents
            if exponent <= 10000:
                start_simple = time.perf_counter()
                res_simple = simple_pow(base, exponent, mod)
                end_simple = time.perf_counter()
                print(f"Проверка наивным алгоритмом: результат = {res_simple}")
                print(f"⏱ Время наивного алгоритма: {end_simple - start_simple:.6f} сек")
                if res_fast != res_simple:
                    print("Ошибка: результаты не совпадают!")
                else:
                    print("✓ Результаты совпадают.\n")
            else:
                print("Показатель слишком велик для наивной проверки (пропускаем).\n")

        except ValueError:
            print("Ошибка ввода. Введите целые числа.\n")
            continue

        cont = input("Продолжить? (y/n): ").strip().lower()
        if cont != 'y':
            break
        print()

    print("Программа завершена.")

if __name__ == "__main__":
    main()
