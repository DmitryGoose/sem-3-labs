"""
Тесты с использованием Mock-объектов
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, call
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coffee import Coffee
from factory import SimpleCoffeeFactory, CoffeeFactory
from decorator import MilkDecorator
from observer import Order, OrderStatus, OrderObserver, CustomerNotifier


class TestMockCoffee(unittest.TestCase):
    """Тесты с мок-объектами для Coffee"""

    def test_mock_coffee(self):
        """Тест с мок-объектом кофе"""
        # Создаём мок
        mock_coffee = Mock(spec=Coffee)
        mock_coffee.get_description.return_value = "Мок Кофе"
        mock_coffee.get_cost.return_value = 100.0

        # Проверяем
        self.assertEqual(mock_coffee.get_description(), "Мок Кофе")
        self.assertEqual(mock_coffee.get_cost(), 100.0)

        # Проверяем, что методы были вызваны
        mock_coffee.get_description.assert_called_once()
        mock_coffee.get_cost.assert_called_once()

    def test_decorator_with_mock_coffee(self):
        """Декоратор работает с мок-кофе"""
        mock_coffee = Mock(spec=Coffee)
        mock_coffee.get_description.return_value = "Базовый"
        mock_coffee.get_cost.return_value = 100.0

        # Применяем декоратор
        decorated = MilkDecorator(mock_coffee)

        # Проверяем
        self.assertEqual(decorated.get_cost(), 130.0)  # 100 + 30
        self.assertIn("молоко", decorated.get_description())


class TestMockObserver(unittest.TestCase):
    """Тесты Observer с мок-объектами"""

    def test_observer_called_on_status_change(self):
        """Наблюдатель вызывается при изменении статуса"""
        order = Order("Эспрессо", "Тест")

        # Создаём мок-наблюдателя
        mock_observer = Mock(spec=OrderObserver)
        order.attach(mock_observer)

        # Меняем статус
        order.set_status(OrderStatus.PREPARING, "Готовим")

        # Проверяем вызов
        mock_observer.update.assert_called_once_with(
            order.id,
            OrderStatus.PREPARING,
            "Готовим"
        )

    def test_multiple_status_changes(self):
        """Проверка множественных изменений статуса"""
        order = Order("Латте", "Тест")
        mock_observer = Mock(spec=OrderObserver)
        order.attach(mock_observer)

        # Меняем статусы
        order.set_status(OrderStatus.PREPARING)
        order.set_status(OrderStatus.READY)
        order.set_status(OrderStatus.DELIVERED)

        # Проверяем количество вызовов
        self.assertEqual(mock_observer.update.call_count, 3)

        # Проверяем последовательность вызовов
        calls = mock_observer.update.call_args_list
        self.assertEqual(calls[0][0][1], OrderStatus.PREPARING)
        self.assertEqual(calls[1][0][1], OrderStatus.READY)
        self.assertEqual(calls[2][0][1], OrderStatus.DELIVERED)

    def test_detached_observer_not_called(self):
        """Отключённый наблюдатель не вызывается"""
        order = Order("Капучино", "Тест")
        mock_observer = Mock(spec=OrderObserver)

        order.attach(mock_observer)
        order.detach(mock_observer)
        order.set_status(OrderStatus.READY)

        mock_observer.update.assert_not_called()


class TestMockFactory(unittest.TestCase):
    """Тесты Factory с мок-объектами"""

    @patch.object(SimpleCoffeeFactory, 'create')
    def test_patched_factory(self, mock_create):
        """Патчинг фабричного метода"""
        mock_coffee = Mock(spec=Coffee)
        mock_coffee.get_description.return_value = "Патченый кофе"
        mock_create.return_value = mock_coffee

        # Вызываем
        result = SimpleCoffeeFactory.create('anything')

        # Проверяем
        self.assertEqual(result.get_description(), "Патченый кофе")
        mock_create.assert_called_once_with('anything')


class TestMockNotificationService(unittest.TestCase):
    """Тесты с мок-сервисом уведомлений"""

    def test_notification_sent(self):
        """Уведомление отправляется"""
        # Создаём мок для внешнего сервиса
        mock_sms_service = Mock()
        mock_sms_service.send.return_value = True

        # Симулируем отправку
        order_id = 1
        message = "Ваш заказ готов!"

        result = mock_sms_service.send(order_id, message)

        self.assertTrue(result)
        mock_sms_service.send.assert_called_with(1, "Ваш заказ готов!")

    def test_notification_failure_handling(self):
        """Обработка ошибки отправки"""
        mock_sms_service = Mock()
        mock_sms_service.send.side_effect = Exception("Сервис недоступен")

        with self.assertRaises(Exception) as context:
            mock_sms_service.send(1, "Тест")

        self.assertIn("Сервис недоступен", str(context.exception))


class TestMockWithMagicMock(unittest.TestCase):
    """Тесты с MagicMock"""

    def test_magic_mock_coffee_shop(self):
        """MagicMock для кофейни"""
        mock_shop = MagicMock()

        # MagicMock автоматически создаёт атрибуты
        mock_shop.name = "Тестовая кофейня"
        mock_shop.create_order.return_value = Mock(id=1)
        mock_shop.orders = []

        # Используем
        order = mock_shop.create_order("Иван", "espresso")
        mock_shop.orders.append(order)

        # Проверяем
        self.assertEqual(order.id, 1)
        mock_shop.create_order.assert_called_once_with("Иван", "espresso")


class TestPatchDecorator(unittest.TestCase):
    """Тесты с декоратором @patch"""

    @patch('observer.datetime')
    def test_logger_timestamp(self, mock_datetime):
        """Патчинг datetime в логгере"""
        from observer import OrderLogger

        mock_datetime.now.return_value.strftime.return_value = "2024-01-01 12:00:00"

        logger = OrderLogger()
        order = Order("Эспрессо", "Тест")
        order.attach(logger)
        order.set_status(OrderStatus.READY)

        self.assertTrue(len(logger.logs) > 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)