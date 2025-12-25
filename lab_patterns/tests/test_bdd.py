"""
BDD-style тесты с использованием pytest

Для полноценного BDD используйте pytest-bdd или behave.
Здесь показан упрощённый BDD-подход.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coffee import Espresso, Latte
from factory import SimpleCoffeeFactory
from decorator import MilkDecorator, SyrupDecorator, WhippedCreamDecorator
from observer import Order, OrderStatus, CustomerNotifier


# ============== Сценарий 1: Заказ простого кофе ==============

class TestOrderSimpleCoffee:
    """
    Feature: Заказ простого кофе
    As a клиент кофейни
    I want заказать эспрессо
    So that я могу получить свой напиток
    """

    def test_scenario_order_espresso(self):
        """
        Scenario: Заказ эспрессо
        Given у меня есть фабрика кофе
        When я заказываю эспрессо
        Then я получаю эспрессо стоимостью 150 рублей
        """
        # Given
        factory = SimpleCoffeeFactory

        # When
        coffee = factory.create('espresso')

        # Then
        assert coffee.get_description() == "Эспрессо"
        assert coffee.get_cost() == 150.0


# ============== Сценарий 2: Кофе с добавками ==============

class TestCoffeeWithAdditions:
    """
    Feature: Кофе с добавками
    As a клиент
    I want добавить молоко и сироп в латте
    So that мой напиток будет вкуснее
    """

    def test_scenario_latte_with_additions(self):
        """
        Scenario: Латте с молоком и карамельным сиропом
        Given у меня есть латте
        When я добавляю молоко
        And я добавляю карамельный сироп
        Then стоимость увеличивается на 80 рублей
        And описание содержит все добавки
        """
        # Given
        coffee = Latte()
        initial_cost = coffee.get_cost()

        # When
        coffee = MilkDecorator(coffee)
        coffee = SyrupDecorator(coffee, 'caramel')

        # Then
        expected_increase = 30.0 + 50.0  # milk + caramel syrup
        assert coffee.get_cost() == initial_cost + expected_increase
        assert "молоко" in coffee.get_description()
        assert "карамельный сироп" in coffee.get_description()


# ============== Сценарий 3: Уведомления о заказе ==============

class TestOrderNotifications:
    """
    Feature: Уведомления о заказе
    As a клиент
    I want получать SMS о статусе заказа
    So that я знаю когда забрать кофе
    """

    def test_scenario_receive_notification_when_ready(self):
        """
        Scenario: Получение уведомления о готовности
        Given я сделал заказ на капучино
        And я подписался на SMS-уведомления
        When бариста готовит заказ
        And заказ готов
        Then я получаю 2 уведомления
        And последнее уведомление содержит статус "готов"
        """
        # Given
        order = Order("Капучино", "Клиент")
        notifier = CustomerNotifier("sms")
        order.attach(notifier)

        # When
        order.set_status(OrderStatus.PREPARING)
        order.set_status(OrderStatus.READY)

        # Then
        assert len(notifier.notifications) == 2
        assert "готов" in notifier.notifications[-1]


# ============== Сценарий 4: Отмена заказа ==============

class TestOrderCancellation:
    """
    Feature: Отмена заказа
    As a клиент
    I want отменить заказ
    So that я не плачу за ненужный напиток
    """

    def test_scenario_cancel_order(self):
        """
        Scenario: Отмена заказа до приготовления
        Given я сделал заказ
        When я отменяю заказ
        Then статус заказа становится "отменён"
        """
        # Given
        order = Order("Латте", "Клиент")

        # When
        order.set_status(OrderStatus.CANCELLED)

        # Then
        assert order.status == OrderStatus.CANCELLED


# ============== Примеры параметризованных тестов ==============

class TestCoffeeTypes:
    """Параметризованные тесты для разных типов кофе"""

    @pytest.mark.parametrize("coffee_type,expected_min_cost", [
        ("espresso", 100),
        ("americano", 100),
        ("cappuccino", 200),
        ("latte", 200),
    ])
    def test_coffee_minimum_cost(self, coffee_type, expected_min_cost):
        """
        Scenario Outline: Проверка минимальной стоимости
        Given я заказываю <coffee_type>
        Then стоимость не меньше <expected_min_cost> рублей
        """
        coffee = SimpleCoffeeFactory.create(coffee_type)
        assert coffee.get_cost() >= expected_min_cost


if __name__ == '__main__':
    pytest.main([__file__, '-v'])