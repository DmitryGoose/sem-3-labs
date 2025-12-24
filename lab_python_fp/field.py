# Пример:
# goods = [
#    {'title': 'Ковер', 'price': 2000, 'color': 'green'},
#    {'title': 'Диван для отдыха', 'price': 5300, 'color': 'black'}
# ]
# field(goods, 'title') должен выдавать 'Ковер', 'Диван для отдыха'
# field(goods, 'title', 'price') должен выдавать {'title': 'Ковер', 'price': 2000}, {'title': 'Диван для отдыха', 'price': 5300}

def field(items, *args):
    assert len(args) > 0

    for item in items:
        if len(args) == 1:
            # Один аргумент - возвращаем только значение
            value = item.get(args[0])
            if value is not None:
                yield value
        else:
            # Несколько аргументов - возвращаем словарь
            result = {}
            for key in args:
                value = item.get(key)
                if value is not None:
                    result[key] = value
            if result:  # Если словарь не пустой
                yield result


if __name__ == '__main__':
    goods = [
        {'title': 'Ковер', 'price': 2000, 'color': 'green'},
        {'title': 'Диван для отдыха', 'color': 'black'}
    ]

    print("Тест 1: field(goods, 'title')")
    for item in field(goods, 'title'):
        print(f"  {item}")

    print("\nТест 2: field(goods, 'title', 'price')")
    for item in field(goods, 'title', 'price'):
        print(f"  {item}")

    print("\nТест 3: field(goods, 'price')")
    for item in field(goods, 'price'):
        print(f"  {item}")