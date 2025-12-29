"""
Рубежный контроль №2 - Модульные тесты
Тестирование с использованием unittest (TDD-фреймворк)
"""

import unittest
from rk1_refactored import (
    Street, House, HouseStreet,
    get_streets_with_keyword,
    get_houses_by_street,
    calculate_avg_cost,
    query_streets_with_houses,
    query_streets_avg_cost_sorted,
    get_houses_starting_with,
    query_houses_with_streets_many_to_many
)


class TestStreetFiltering(unittest.TestCase):
    """Тесты для фильтрации улиц (Запрос 1)"""
    
    def setUp(self):
        """Подготовка тестовых данных перед каждым тестом."""
        self.streets = [
            Street(1, "Улица Абрикосовая"),
            Street(2, "Проспект Мира"),
            Street(3, "Улица отдел связи"),
            Street(4, "Переулок отдел кадров"),
            Street(5, "Улица Академическая")
        ]
        
        self.houses = [
            House(1, "Дом Александровых", 5500000.0, 1),
            House(2, "Дом Петровых", 3200000.0, 1),
            House(3, "Дом Антонович", 4800000.0, 2),
            House(4, "Дом Сидоровых", 6100000.0, 3),
            House(5, "Дом Алексеевых", 2900000.0, 3),
        ]
    
    def test_get_streets_with_keyword_found(self):
        """Тест: поиск улиц с ключевым словом 'отдел' - находит 2 улицы."""
        result = get_streets_with_keyword(self.streets, "отдел")
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].name, "Улица отдел связи")
        self.assertEqual(result[1].name, "Переулок отдел кадров")
    
    def test_get_streets_with_keyword_not_found(self):
        """Тест: поиск улиц с несуществующим ключевым словом - пустой список."""
        result = get_streets_with_keyword(self.streets, "несуществующее")
        
        self.assertEqual(len(result), 0)
        self.assertIsInstance(result, list)
    
    def test_get_streets_with_keyword_case_insensitive(self):
        """Тест: поиск регистронезависимый."""
        result_lower = get_streets_with_keyword(self.streets, "отдел")
        result_upper = get_streets_with_keyword(self.streets, "ОТДЕЛ")
        result_mixed = get_streets_with_keyword(self.streets, "ОтДеЛ")
        
        self.assertEqual(len(result_lower), len(result_upper))
        self.assertEqual(len(result_lower), len(result_mixed))
    
    def test_query_streets_with_houses(self):
        """Тест: запрос 1 - улицы с 'отдел' и их дома."""
        result = query_streets_with_houses(self.streets, self.houses, "отдел")
        
        self.assertEqual(len(result), 2)
        
        # Проверяем первую улицу
        street_name, house_list = result[0]
        self.assertEqual(street_name, "Улица отдел связи")
        self.assertIn("Дом Сидоровых", house_list)
        self.assertIn("Дом Алексеевых", house_list)


class TestAverageCostCalculation(unittest.TestCase):
    """Тесты для расчёта средней стоимости (Запрос 2)"""
    
    def setUp(self):
        """Подготовка тестовых данных."""
        self.streets = [
            Street(1, "Улица Тестовая"),
            Street(2, "Улица Пустая"),
            Street(3, "Улица Одинокая")
        ]
        
        self.houses = [
            House(1, "Дом 1", 1000000.0, 1),
            House(2, "Дом 2", 2000000.0, 1),
            House(3, "Дом 3", 3000000.0, 1),
            House(4, "Дом 4", 5000000.0, 3),
        ]
    
    def test_calculate_avg_cost_multiple_houses(self):
        """Тест: средняя стоимость для улицы с несколькими домами."""
        result = calculate_avg_cost(self.houses, street_id=1)
        
        expected = (1000000.0 + 2000000.0 + 3000000.0) / 3
        self.assertEqual(result, round(expected, 2))
        self.assertEqual(result, 2000000.0)
    
    def test_calculate_avg_cost_no_houses(self):
        """Тест: средняя стоимость для улицы без домов = 0."""
        result = calculate_avg_cost(self.houses, street_id=2)
        
        self.assertEqual(result, 0.0)
    
    def test_calculate_avg_cost_single_house(self):
        """Тест: средняя стоимость для улицы с одним домом."""
        result = calculate_avg_cost(self.houses, street_id=3)
        
        self.assertEqual(result, 5000000.0)
    
    def test_query_streets_avg_cost_sorted(self):
        """Тест: запрос 2 - сортировка по средней стоимости."""
        result = query_streets_avg_cost_sorted(self.streets, self.houses)
        
        # Должно быть 2 улицы (Пустая исключена)
        self.assertEqual(len(result), 2)
        
        # Проверяем сортировку по возрастанию
        self.assertEqual(result[0][0], "Улица Тестовая")  # 2000000
        self.assertEqual(result[1][0], "Улица Одинокая")  # 5000000
        
        # Проверяем, что первая стоимость меньше второй
        self.assertLess(result[0][1], result[1][1])


class TestManyToManyRelation(unittest.TestCase):
    """Тесты для связи многие-ко-многим (Запрос 3)"""
    
    def setUp(self):
        """Подготовка тестовых данных."""
        self.streets = [
            Street(1, "Улица Первая"),
            Street(2, "Улица Вторая"),
            Street(3, "Улица Третья")
        ]
        
        self.houses = [
            House(1, "Дом Александровых", 1000000.0, 1),
            House(2, "Дом Борисовых", 2000000.0, 1),
            House(3, "Дом Антоновых", 3000000.0, 2),
        ]
        
        self.house_streets = [
            HouseStreet(1, 1),
            HouseStreet(1, 2),  # Дом Александровых на 2 улицах
            HouseStreet(2, 1),
            HouseStreet(3, 2),
            HouseStreet(3, 3),  # Дом Антоновых на 2 улицах
        ]
    
    def test_get_houses_starting_with_letter(self):
        """Тест: фильтрация домов по начальной букве."""
        result = get_houses_starting_with(self.houses, "А")
        
        self.assertEqual(len(result), 2)
        addresses = [h.address for h in result]
        self.assertIn("Дом Александровых", addresses)
        self.assertIn("Дом Антоновых", addresses)
    
    def test_get_houses_starting_with_no_match(self):
        """Тест: фильтрация по букве без совпадений."""
        result = get_houses_starting_with(self.houses, "Я")
        
        self.assertEqual(len(result), 0)
    
    def test_query_many_to_many(self):
        """Тест: запрос 3 - дома на 'А' и их улицы через связь M:N."""
        result = query_houses_with_streets_many_to_many(
            self.houses, self.streets, self.house_streets, "А"
        )
        
        # Должно быть 2 дома
        self.assertEqual(len(result), 2)
        
        # Проверяем Дом Александровых
        self.assertIn("Дом Александровых", result)
        self.assertEqual(len(result["Дом Александровых"]), 2)
        self.assertIn("Улица Первая", result["Дом Александровых"])
        self.assertIn("Улица Вторая", result["Дом Александровых"])
        
        # Проверяем Дом Антоновых
        self.assertIn("Дом Антоновых", result)
        self.assertEqual(len(result["Дом Антоновых"]), 2)


class TestEdgeCases(unittest.TestCase):
    """Тесты граничных случаев"""
    
    def test_empty_streets_list(self):
        """Тест: пустой список улиц."""
        result = get_streets_with_keyword([], "отдел")
        self.assertEqual(result, [])
    
    def test_empty_houses_list(self):
        """Тест: пустой список домов."""
        result = calculate_avg_cost([], street_id=1)
        self.assertEqual(result, 0.0)
    
    def test_query_with_empty_data(self):
        """Тест: запрос с пустыми данными."""
        result = query_streets_with_houses([], [], "отдел")
        self.assertEqual(result, [])


if __name__ == "__main__":
    # Запуск тестов с подробным выводом
    unittest.main(verbosity=2)