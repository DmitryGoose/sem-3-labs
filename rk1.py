from dataclasses import dataclass
from itertools import groupby

# Класс "Улица" (аналог "Отдел")
@dataclass
class Street:
    street_id: int
    name: str

# Класс "Дом" (аналог "Сотрудник") с количественным признаком - стоимость
@dataclass
class House:
    house_id: int
    address: str  # Название/номер дома
    cost: float   # Стоимость дома (количественный признак)
    street_id: int  # Внешний ключ для связи один-ко-многим

# Класс для связи многие-ко-многим "Дома на улице"
@dataclass
class HouseStreet:
    house_id: int
    street_id: int

# Создание тестовых данных для улиц
streets = [
    Street(1, "Улица Абрикосовая"),
    Street(2, "Проспект Мира"),
    Street(3, "Улица отдел связи"),
    Street(4, "Переулок отдел кадров"),
    Street(5, "Улица Академическая")
]

# Создание тестовых данных для домов (с количественным признаком - стоимость)
houses = [
    House(1, "Дом Александровых", 5500000.0, 1),
    House(2, "Дом Петровых", 3200000.0, 1),
    House(3, "Дом Антонович", 4800000.0, 2),
    House(4, "Дом Сидоровых", 6100000.0, 3),
    House(5, "Дом Алексеевых", 2900000.0, 3),
    House(6, "Дом Козловых", 7500000.0, 4),
    House(7, "Дом Андреевых", 4100000.0, 5)
]

# Связь многие-ко-многим
house_streets = [
    HouseStreet(1, 1),
    HouseStreet(1, 3),
    HouseStreet(2, 1),
    HouseStreet(3, 2),
    HouseStreet(3, 5),
    HouseStreet(4, 3),
    HouseStreet(5, 3),
    HouseStreet(5, 4),
    HouseStreet(6, 4),
    HouseStreet(7, 5),
    HouseStreet(7, 1)
]

print("=" * 70)
print("РУБЕЖНЫЙ КОНТРОЛЬ №1 - ВАРИАНТ 6 (Дом - Улица)")
print("Вариант запросов: Е")
print("=" * 70)

# ============================================================================
# ЗАПРОС 1: Связь один-ко-многим
# Вывести список всех улиц, у которых в названии присутствует слово "отдел",
# и список находящихся на них домов
# ============================================================================
print("\n" + "=" * 70)
print("ЗАПРОС 1 (один-ко-многим):")
print("Улицы, в названии которых присутствует слово 'отдел', и их дома")
print("=" * 70)

# Фильтрация улиц с помощью list comprehension
streets_with_otdel = [s for s in streets if "отдел" in s.name.lower()]

# Получение домов для каждой улицы
result_1 = [
    (street.name, [h.address for h in houses if h.street_id == street.street_id])
    for street in streets_with_otdel
]

for street_name, house_list in result_1:
    print(f"\nУлица: {street_name}")
    print(f"  Дома: {', '.join(house_list) if house_list else 'Нет домов'}")

# ============================================================================
# ЗАПРОС 2: Связь один-ко-многим
# Вывести список улиц со средней стоимостью домов на каждой улице,
# отсортированный по средней стоимости (округление до 2 знаков)
# ============================================================================
print("\n" + "=" * 70)
print("ЗАПРОС 2 (один-ко-многим):")
print("Улицы со средней стоимостью домов, отсортированные по средней стоимости")
print("=" * 70)

# Вычисление средней стоимости для каждой улицы
def calculate_avg_cost(street_id):
    street_houses = [h.cost for h in houses if h.street_id == street_id]
    if street_houses:
        return round(sum(street_houses) / len(street_houses), 2)
    return 0.0

# Формирование списка с помощью list comprehension
result_2 = [
    (street.name, calculate_avg_cost(street.street_id))
    for street in streets
]

# Фильтрация улиц без домов и сортировка по средней стоимости
result_2_filtered = sorted(
    [(name, avg) for name, avg in result_2 if avg > 0],
    key=lambda x: x[1]
)

print(f"\n{'Улица':<30} {'Средняя стоимость (руб.)':<25}")
print("-" * 55)
for street_name, avg_cost in result_2_filtered:
    print(f"{street_name:<30} {avg_cost:>20,.2f}")

# ============================================================================
# ЗАПРОС 3: Связь многие-ко-многим
# Вывести список всех домов, у которых название начинается с буквы "А",
# и названия их улиц
# ============================================================================
print("\n" + "=" * 70)
print("ЗАПРОС 3 (многие-ко-многим):")
print("Дома, название которых начинается с буквы 'А', и их улицы")
print("=" * 70)

# Создание словаря для быстрого поиска улиц по ID
street_dict = {s.street_id: s.name for s in streets}

# Создание словаря для быстрого поиска домов по ID
house_dict = {h.house_id: h for h in houses}

# Фильтрация домов, название которых начинается с "А"
houses_starting_with_a = [h for h in houses if h.address.startswith("А") or
                          h.address.split()[-1].startswith("А")]

# Более точная фильтрация - проверяем фамилию/название
houses_starting_with_a = [
    h for h in houses
    if any(word.startswith("А") for word in h.address.split())
]

# Получение связей многие-ко-многим для отфильтрованных домов
result_3 = [
    (house_dict[hs.house_id].address, street_dict[hs.street_id])
    for hs in house_streets
    if hs.house_id in [h.house_id for h in houses_starting_with_a]
]

# Группировка по домам
result_3_grouped = {}
for house_name, street_name in result_3:
    if house_name not in result_3_grouped:
        result_3_grouped[house_name] = []
    result_3_grouped[house_name].append(street_name)

print(f"\n{'Дом':<25} {'Улицы':<45}")
print("-" * 70)
for house_name, street_list in result_3_grouped.items():
    print(f"{house_name:<25} {', '.join(street_list):<45}")

# ============================================================================
# Дополнительный вывод исходных данных для проверки
# ============================================================================
print("\n" + "=" * 70)
print("ИСХОДНЫЕ ДАННЫЕ")
print("=" * 70)

print("\nСписок улиц:")
print("-" * 40)
for s in streets:
    print(f"  ID: {s.street_id}, Название: {s.name}")

print("\nСписок домов:")
print("-" * 60)
for h in houses:
    print(f"  ID: {h.house_id}, Название: {h.address}, "
          f"Стоимость: {h.cost:,.0f} руб., ID улицы: {h.street_id}")

print("\nСвязи многие-ко-многим (Дом - Улица):")
print("-" * 50)
for hs in house_streets:
    house_name = house_dict[hs.house_id].address
    street_name = street_dict[hs.street_id]
    print(f"  {house_name} <-> {street_name}")
