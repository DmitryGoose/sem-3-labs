"""
Рубежный контроль №1 - Рефакторинг для модульного тестирования
Вариант 6: Дом - Улица
"""

from dataclasses import dataclass
from typing import List, Tuple, Dict


@dataclass
class Street:
    """Класс Улица"""
    street_id: int
    name: str


@dataclass
class House:
    """Класс Дом с количественным признаком - стоимость"""
    house_id: int
    address: str
    cost: float
    street_id: int


@dataclass
class HouseStreet:
    """Класс для связи многие-ко-многим"""
    house_id: int
    street_id: int


# ============================================================================
# ФУНКЦИИ ДЛЯ ЗАПРОСОВ (вынесены для тестирования)
# ============================================================================

def get_streets_with_keyword(streets: List[Street], keyword: str) -> List[Street]:
    """
    Фильтрует улицы по ключевому слову в названии.
    
    Args:
        streets: Список улиц
        keyword: Ключевое слово для поиска (регистронезависимо)
    
    Returns:
        Список улиц, содержащих ключевое слово
    """
    return [s for s in streets if keyword.lower() in s.name.lower()]


def get_houses_by_street(houses: List[House], street_id: int) -> List[House]:
    """
    Возвращает дома на указанной улице (связь один-ко-многим).
    
    Args:
        houses: Список всех домов
        street_id: ID улицы
    
    Returns:
        Список домов на данной улице
    """
    return [h for h in houses if h.street_id == street_id]


def query_streets_with_houses(
    streets: List[Street], 
    houses: List[House], 
    keyword: str
) -> List[Tuple[str, List[str]]]:
    """
    ЗАПРОС 1: Улицы с ключевым словом и их дома.
    
    Args:
        streets: Список улиц
        houses: Список домов
        keyword: Ключевое слово для фильтрации улиц
    
    Returns:
        Список кортежей (название_улицы, [список_адресов_домов])
    """
    filtered_streets = get_streets_with_keyword(streets, keyword)
    
    return [
        (street.name, [h.address for h in get_houses_by_street(houses, street.street_id)])
        for street in filtered_streets
    ]


def calculate_avg_cost(houses: List[House], street_id: int) -> float:
    """
    Вычисляет среднюю стоимость домов на улице.
    
    Args:
        houses: Список всех домов
        street_id: ID улицы
    
    Returns:
        Средняя стоимость (округлённая до 2 знаков) или 0.0
    """
    street_houses = [h.cost for h in houses if h.street_id == street_id]
    if street_houses:
        return round(sum(street_houses) / len(street_houses), 2)
    return 0.0


def query_streets_avg_cost_sorted(
    streets: List[Street], 
    houses: List[House]
) -> List[Tuple[str, float]]:
    """
    ЗАПРОС 2: Улицы со средней стоимостью домов, отсортированные по стоимости.
    
    Args:
        streets: Список улиц
        houses: Список домов
    
    Returns:
        Отсортированный список кортежей (название_улицы, средняя_стоимость)
    """
    result = [
        (street.name, calculate_avg_cost(houses, street.street_id))
        for street in streets
    ]
    
    # Фильтруем улицы без домов и сортируем
    return sorted(
        [(name, avg) for name, avg in result if avg > 0],
        key=lambda x: x[1]
    )


def get_houses_starting_with(houses: List[House], letter: str) -> List[House]:
    """
    Фильтрует дома, в названии которых есть слово, начинающееся с указанной буквы.
    
    Args:
        houses: Список домов
        letter: Начальная буква
    
    Returns:
        Отфильтрованный список домов
    """
    return [
        h for h in houses
        if any(word.startswith(letter) for word in h.address.split())
    ]


def query_houses_with_streets_many_to_many(
    houses: List[House],
    streets: List[Street],
    house_streets: List[HouseStreet],
    letter: str
) -> Dict[str, List[str]]:
    """
    ЗАПРОС 3: Дома, начинающиеся с буквы, и их улицы (многие-ко-многим).
    
    Args:
        houses: Список домов
        streets: Список улиц
        house_streets: Связи многие-ко-многим
        letter: Начальная буква для фильтрации
    
    Returns:
        Словарь {название_дома: [список_улиц]}
    """
    street_dict = {s.street_id: s.name for s in streets}
    house_dict = {h.house_id: h for h in houses}
    
    filtered_houses = get_houses_starting_with(houses, letter)
    filtered_house_ids = {h.house_id for h in filtered_houses}
    
    result = {}
    for hs in house_streets:
        if hs.house_id in filtered_house_ids:
            house_name = house_dict[hs.house_id].address
            street_name = street_dict[hs.street_id]
            
            if house_name not in result:
                result[house_name] = []
            result[house_name].append(street_name)
    
    return result


# ============================================================================
# ТЕСТОВЫЕ ДАННЫЕ
# ============================================================================

def get_test_data():
    """Возвращает тестовые данные для демонстрации и тестирования."""
    
    streets = [
        Street(1, "Улица Абрикосовая"),
        Street(2, "Проспект Мира"),
        Street(3, "Улица отдел связи"),
        Street(4, "Переулок отдел кадров"),
        Street(5, "Улица Академическая")
    ]
    
    houses = [
        House(1, "Дом Александровых", 5500000.0, 1),
        House(2, "Дом Петровых", 3200000.0, 1),
        House(3, "Дом Антонович", 4800000.0, 2),
        House(4, "Дом Сидоровых", 6100000.0, 3),
        House(5, "Дом Алексеевых", 2900000.0, 3),
        House(6, "Дом Козловых", 7500000.0, 4),
        House(7, "Дом Андреевых", 4100000.0, 5)
    ]
    
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
    
    return streets, houses, house_streets


# ============================================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================================

def main():
    """Основная функция для демонстрации работы запросов."""
    
    streets, houses, house_streets = get_test_data()
    
    print("=" * 70)
    print("РУБЕЖНЫЙ КОНТРОЛЬ №1 - ВАРИАНТ 6 (Дом - Улица)")
    print("=" * 70)
    
    # Запрос 1
    print("\n" + "=" * 70)
    print("ЗАПРОС 1: Улицы со словом 'отдел' и их дома")
    print("=" * 70)
    
    result_1 = query_streets_with_houses(streets, houses, "отдел")
    for street_name, house_list in result_1:
        print(f"\nУлица: {street_name}")
        print(f"  Дома: {', '.join(house_list) if house_list else 'Нет домов'}")
    
    # Запрос 2
    print("\n" + "=" * 70)
    print("ЗАПРОС 2: Улицы со средней стоимостью домов")
    print("=" * 70)
    
    result_2 = query_streets_avg_cost_sorted(streets, houses)
    print(f"\n{'Улица':<30} {'Средняя стоимость':<20}")
    print("-" * 50)
    for street_name, avg_cost in result_2:
        print(f"{street_name:<30} {avg_cost:>15,.2f} руб.")
    
    # Запрос 3
    print("\n" + "=" * 70)
    print("ЗАПРОС 3: Дома на букву 'А' и их улицы (многие-ко-многим)")
    print("=" * 70)
    
    result_3 = query_houses_with_streets_many_to_many(houses, streets, house_streets, "А")
    print(f"\n{'Дом':<25} {'Улицы':<45}")
    print("-" * 70)
    for house_name, street_list in result_3.items():
        print(f"{house_name:<25} {', '.join(street_list)}")


if __name__ == "__main__":
    main()