"""
TDD тесты с использованием unittest
"""

import unittest
import sys
import os

# Добавляем родительскую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coffee import Espresso, Americano, Cappuccino, Latte
from factory import SimpleCoffeeFactory, EspressoFactory
from decorator import MilkDecorator, SugarDecorator, SyrupDecorator
from observer import Order, OrderStatus, CustomerNotifier, OrderLogger


class TestCoffee(unittest.TestCase):
    """Тесты для базовых классов кофе"""

    def test_espresso_cost(self):
        """Эспрессо стоит 150 рублей"""
        coffee = Espresso()
        self.assertEqual(coffee.get_cost(), 150.0)

    def test_espresso_description(self):
        """Описание эспрессо"""
        coffee = Espresso()
        self.assertEqual(coffee.get_description(), "Эспрессо")

    def test_all_coffees_have_positive_cost(self):
        """Все виды кофе имеют положительную стоимость"""
        coffees = [Espresso(), Americano(), Cappuccino(), Latte()]
        for coffee in coffees:
            self.assertGreater(coffee.get_cost(), 0)


class TestFactory(unittest.TestCase):
    """Тесты для фабрики кофе"""

    def test_create_espresso(self):
        """Фабрика создаёт эспрессо"""
        coffee = SimpleCoffeeFactory.create('espresso')
        self.assertIsInstance(coffee, Espresso)

    def test_create_latte(self):
        """Фабрика создаёт латте"""
        coffee = SimpleCoffeeFactory.create('latte')
        self.assertIsInstance(coffee, Latte)

    def test_unknown_coffee_raises_error(self):
        """Неизвестный тип кофе вызывает ошибку"""
        with self.assertRaises(ValueError):
            SimpleCoffeeFactory.create('unknown')

    def test_case_insensitive(self):
        """Фабрика нечувствительна к регистру"""
        coffee1 = SimpleCoffeeFactory.create('ESPRESSO')
        coffee2 = SimpleCoffeeFactory.create('Espresso')
        self.assertIsInstance(coffee1, Espresso)
        self.assertIsInstance(coffee2, Espresso)

    def test_available_types(self):
        """Список доступных типов"""
        types = SimpleCoffeeFactory.get_available_types()
        self.assertIn('espresso', types)
        self.assertIn('latte', types)


class TestDecorator(unittest.TestCase):
    """Тесты для декораторов"""

    def test_milk_adds_cost(self):
        """Молоко добавляет 30 рублей"""
        coffee = Espresso()
        coffee_with_milk = MilkDecorator(coffee)
        self.assertEqual(coffee_with_milk.get_cost(), 150.0 + 30.0)

    def test_milk_adds_description(self):
        """Молоко добавляется в описание"""
        coffee = MilkDecorator(Espresso())
        self.assertIn("молоко", coffee.get_description())

    def test_multiple_decorators(self):
        """Несколько декораторов работают вместе"""
        coffee = SugarDecorator(MilkDecorator(Espresso()))
        expected_cost = 150.0 + 30.0 + 10.0  # espresso + milk + sugar
        self.assertEqual(coffee.get_cost(), expected_cost)

    def test_syrup_decorator(self):
        """Сироп добавляет стоимость"""
        coffee = SyrupDecorator(Espresso(), 'vanilla')
        self.assertEqual(coffee.get_cost(), 150.0 + 50.0)

    def test_invalid_syrup_raises_error(self):
        """Неизвестный сироп вызывает ошибку"""
        with self.assertRaises(ValueError):
            SyrupDecorator(Espresso(), 'unknown')


class TestObserver(unittest.TestCase):
    """Тесты для паттерна Observer"""

    def test_order_creation(self):
        """Заказ создаётся с правильными данными"""
        order = Order("Эспрессо", "Иван")
        self.assertEqual(order.coffee, "Эспрессо")
        self.assertEqual(order.customer, "Иван")
        self.assertEqual(order.status, OrderStatus.CREATED)

    def test_observer_attached(self):
        """Наблюдатель подключается"""
        order = Order("Эспрессо", "Иван")
        notifier = CustomerNotifier()
        order.attach(notifier)

        order.set_status(OrderStatus.PREPARING)

        self.assertEqual(len(notifier.notifications), 1)

    def test_observer_detached(self):
        """Наблюдатель отключается"""
        order = Order("Эспрессо", "Иван")
        notifier = CustomerNotifier()
        order.attach(notifier)
        order.detach(notifier)

        order.set_status(OrderStatus.PREPARING)

        self.assertEqual(len(notifier.notifications), 0)

    def test_multiple_observers(self):
        """Несколько наблюдателей получают уведомления"""
        order = Order("Эспрессо", "Иван")
        notifier1 = CustomerNotifier("sms")
        notifier2 = CustomerNotifier("email")
        logger = OrderLogger()

        order.attach(notifier1)
        order.attach(notifier2)
        order.attach(logger)

        order.set_status(OrderStatus.READY)

        self.assertEqual(len(notifier1.notifications), 1)
        self.assertEqual(len(notifier2.notifications), 1)
        self.assertEqual(len(logger.logs), 1)

    def test_status_flow(self):
        """Правильный поток статусов"""
        order = Order("Эспрессо", "Иван")

        order.set_status(OrderStatus.PREPARING)
        self.assertEqual(order.status, OrderStatus.PREPARING)

        order.set_status(OrderStatus.READY)
        self.assertEqual(order.status, OrderStatus.READY)

        order.set_status(OrderStatus.DELIVERED)
        self.assertEqual(order.status, OrderStatus.DELIVERED)


if __name__ == '__main__':
    unittest.main(verbosity=2)