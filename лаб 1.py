import math
import sys


def read_coefficient(name: str) -> float:
    while True:
        s = input(f"Введите коэффициент {name}: ")
        try:
            value = float(s)
            return value
        except ValueError:
            print(f"Ошибка: '{s}' нельзя преобразовать в число. Повторите ввод.")


def parse_coefficients_from_argv() -> tuple[float | None, float | None, float | None]:
    a = b = c = None

    args = sys.argv[1:]  # пропускаем имя скрипта
    if len(args) >= 1:
        try:
            a = float(args[0])
        except ValueError:
            print(f"Предупреждение: параметр A='{args[0]}' некорректен и будет запрошен с клавиатуры.")
    if len(args) >= 2:
        try:
            b = float(args[1])
        except ValueError:
            print(f"Предупреждение: параметр B='{args[1]}' некорректен и будет запрошен с клавиатуры.")
    if len(args) >= 3:
        try:
            c = float(args[2])
        except ValueError:
            print(f"Предупреждение: параметр C='{args[2]}' некорректен и будет запрошен с клавиатуры.")

    return a, b, c


def solve_biquadratic(a: float, b: float, c: float) -> list[float]:
    if a == 0:
        raise ValueError("Коэффициент A не должен быть равен нулю (это уже не биквадратное уравнение).")

    D = b * b - 4 * a * c
    print(f"Дискриминант D = {D}")

    roots: list[float] = []

    if D < 0:
        return roots

    if D == 0:
        t = -b / (2 * a)
        print(f"t = {t}")
        if t > 0:
            roots.append(math.sqrt(t))
            roots.append(-math.sqrt(t))
        elif t == 0:
            roots.append(0.0)
        return roots

    # D > 0
    sqrt_D = math.sqrt(D)
    t1 = (-b + sqrt_D) / (2 * a)
    t2 = (-b - sqrt_D) / (2 * a)
    print(f"t1 = {t1}, t2 = {t2}")

    for t in (t1, t2):
        if t > 0:
            roots.append(math.sqrt(t))
            roots.append(-math.sqrt(t))
        elif t == 0:
            roots.append(0.0)

    return roots


def main():
    print("Решение биквадратного уравнения a*x^4 + b*x^2 + c = 0")

    a, b, c = parse_coefficients_from_argv()

    if a is None:
        a = read_coefficient("A")
    if b is None:
        b = read_coefficient("B")
    if c is None:
        c = read_coefficient("C")

    print(f"Используемые коэффициенты: A = {a}, B = {b}, C = {c}")

    try:
        roots = solve_biquadratic(a, b, c)
    except ValueError as e:
        print("Ошибка:", e)
        return

    if not roots:
        print("Действительных корней нет.")
    else:
        roots = sorted(roots)
        print("Действительные корни уравнения:")
        for x in roots:
            print(f"x = {x}")


if __name__ == "__main__":
    main()