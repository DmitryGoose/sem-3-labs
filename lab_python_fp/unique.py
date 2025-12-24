# Итератор для удаления дубликатов
class Unique:
    def __init__(self, items, **kwargs):
        self.items = iter(items)
        self.ignore_case = kwargs.get('ignore_case', False)
        self.seen = set()

    def __next__(self):
        while True:
            item = next(self.items)  # Вызовет StopIteration когда закончатся элементы

            # Определяем ключ для проверки дубликатов
            if self.ignore_case and isinstance(item, str):
                key = item.lower()
            else:
                key = item

            # Если ещё не видели такой элемент
            if key not in self.seen:
                self.seen.add(key)
                return item  # Возвращаем оригинальное значение (не модифицированное)

    def __iter__(self):
        return self


if __name__ == '__main__':
    print("Тест 1: числа с дубликатами")
    data = [1, 1, 1, 1, 1, 2, 2, 2, 2, 2]
    print(f"  Вход: {data}")
    print(f"  Результат: {list(Unique(data))}")

    print("\nТест 2: строки без ignore_case")
    data = ['a', 'A', 'b', 'B', 'a', 'A', 'b', 'B']
    print(f"  Вход: {data}")
    print(f"  Результат: {list(Unique(data))}")

    print("\nТест 3: строки с ignore_case=True")
    data = ['a', 'A', 'b', 'B', 'a', 'A', 'b', 'B']
    print(f"  Вход: {data}")
    print(f"  Результат: {list(Unique(data, ignore_case=True))}")

    print("\nТест 4: с генератором gen_random")
    from gen_random import gen_random

    data = gen_random(10, 1, 3)
    print(f"  Результат: {list(Unique(data))}")