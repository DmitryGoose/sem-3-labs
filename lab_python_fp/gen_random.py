import random


# Пример:
# gen_random(5, 1, 3) должен выдать 5 случайных чисел
# в диапазоне от 1 до 3, например 2, 2, 3, 2, 1

def gen_random(num_count, begin, end):
    for _ in range(num_count):
        yield random.randint(begin, end)


if __name__ == '__main__':
    print("Тест: gen_random(5, 1, 3)")
    result = list(gen_random(5, 1, 3))
    print(f"  Результат: {result}")

    print("\nТест: gen_random(10, 0, 100)")
    result = list(gen_random(10, 0, 100))
    print(f"  Результат: {result}")