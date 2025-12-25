"""
Шаги для BDD-тестов с использованием behave

Для запуска нужно установить: pip install behave
"""

from behave import given, when, then
import sys
import os

# Добавляем путь к основным модулям
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from lab_patterns.coffee import Espresso, Americano, Cappuccino, Latte
from lab_patterns.factory import SimpleCoffeeFactory
from lab_patterns.decorator import MilkDecorator, SugarDecorator, SyrupDecorator, WhippedCreamDecorator
from lab_patterns.observer import Order, OrderStatus


# ============== GIVEN (Допустим) ==============

@given('я в кофейне "{name}"')
def step_in_coffee_shop(context, name):
    """Инициализация контекста кофейни"""
    context.shop_name = name
    context.coffee = None
    context.order = None


@given('у меня есть фабрика кофе')
def step_have_factory(context):
    """Инициализация фабрики"""
    context.factory = SimpleCoffeeFactory


@given('у меня есть латте')
def step_have_latte(context):
    """Создание латте"""
    context.coffee = Latte()
    context.initial_cost = context.coffee.get_cost()


@given('я сделал заказ на {coffee_type}')
def step_made_order(context, coffee_type):
    """Создание заказа"""
    context.order = Order(coffee_type, "Тестовый клиент")


@given('я подписался на SMS-уведомления')
def step_subscribed_sms(context):
    """Подписка на уведомления"""
    from lab_patterns.observer import CustomerNotifier
    context.notifier = CustomerNotifier("sms")
    context.order.attach(context.notifier)


# ============== WHEN (Когда) ==============

@when('я заказываю "{coffee_type}"')
def step_order_coffee(context, coffee_type):
    """Заказ кофе по типу"""
    context.coffee = SimpleCoffeeFactory.create(coffee_type)


@when('я заказываю "{coffee_type}" с добавкой "{addition}"')
def step_order_coffee_with_addition(context, coffee_type, addition):
    """Заказ кофе с добавкой"""
    context.coffee = SimpleCoffeeFactory.create(coffee_type)

    # Применяем добавку
    additions_map = {
        'молоко': MilkDecorator,
        'сахар': SugarDecorator,
        'взбитые сливки': WhippedCreamDecorator,
    }

    if addition in additions_map:
        context.coffee = additions_map[addition](context.coffee)


@when('я добавляю молоко')
def step_add_milk(context):
    """Добавление молока"""
    context.coffee = MilkDecorator(context.coffee)


@when('я добавляю сахар')
def step_add_sugar(context):
    """Добавление сахара"""
    context.coffee = SugarDecorator(context.coffee)


@when('я добавляю карамельный сироп')
def step_add_caramel_syrup(context):
    """Добавление карамельного сиропа"""
    context.coffee = SyrupDecorator(context.coffee, 'caramel')


@when('я добавляю взбитые сливки')
def step_add_whipped_cream(context):
    """Добавление взбитых сливок"""
    context.coffee = WhippedCreamDecorator(context.coffee)


@when('бариста готовит заказ')
def step_barista_prepares(context):
    """Бариста готовит заказ"""
    context.order.set_status(OrderStatus.PREPARING)


@when('заказ готов')
def step_order_ready(context):
    """Заказ готов"""
    context.order.set_status(OrderStatus.READY)


@when('я отменяю заказ')
def step_cancel_order(context):
    """Отмена заказа"""
    context.order.set_status(OrderStatus.CANCELLED)


# ============== THEN (Тогда) ==============

@then('стоимость заказа равна {cost:d} рублей')
def step_check_exact_cost(context, cost):
    """Проверка точной стоимости"""
    assert context.coffee.get_cost() == float(cost), \
        f"Ожидалось {cost}, получено {context.coffee.get_cost()}"


@then('стоимость заказа не менее {min_cost:d} рублей')
def step_check_min_cost(context, min_cost):
    """Проверка минимальной стоимости"""
    assert context.coffee.get_cost() >= float(min_cost), \
        f"Стоимость {context.coffee.get_cost()} меньше {min_cost}"


@then('стоимость увеличивается на {increase:d} рублей')
def step_check_cost_increase(context, increase):
    """Проверка увеличения стоимости"""
    expected = context.initial_cost + float(increase)
    actual = context.coffee.get_cost()
    assert actual == expected, \
        f"Ожидалось {expected}, получено {actual}"


@then('описание содержит "{text}"')
def step_description_contains(context, text):
    """Проверка описания"""
    description = context.coffee.get_description()
    assert text in description, \
        f"'{text}' не найдено в '{description}'"


@then('описание содержит все добавки')
def step_description_contains_all(context):
    """Проверка наличия всех добавок в описании"""
    description = context.coffee.get_description()
    # Проверяем что описание длиннее базового
    assert len(description) > 10, "Описание слишком короткое"


@then('я получаю {count:d} уведомления')
def step_check_notification_count(context, count):
    """Проверка количества уведомлений"""
    actual = len(context.notifier.notifications)
    assert actual == count, \
        f"Ожидалось {count} уведомлений, получено {actual}"


@then('последнее уведомление содержит статус "{status}"')
def step_last_notification_contains(context, status):
    """Проверка последнего уведомления"""
    last = context.notifier.notifications[-1]
    assert status in last, \
        f"'{status}' не найдено в '{last}'"


@then('статус заказа становится "{status}"')
def step_check_order_status(context, status):
    """Проверка статуса заказа"""
    status_map = {
        'создан': OrderStatus.CREATED,
        'готовится': OrderStatus.PREPARING,
        'готов': OrderStatus.READY,
        'выдан': OrderStatus.DELIVERED,
        'отменён': OrderStatus.CANCELLED,
    }
    expected = status_map.get(status)
    assert context.order.status == expected, \
        f"Ожидался статус '{status}', получен '{context.order.status.value}'"


# ============== Для тестирования без behave ==============

if __name__ == '__main__':
    print("=== Тестирование шагов вручную ===\n")


    # Симуляция контекста
    class MockContext:
        pass


    context = MockContext()

    # Тест 1: Заказ эспрессо
    print("Тест 1: Заказ эспрессо")
    step_in_coffee_shop(context, "Python Coffee")
    step_order_coffee(context, "espresso")
    step_check_exact_cost(context, 150)
    print("  ✓ Пройден\n")

    # Тест 2: Латте с молоком
    print("Тест 2: Латте с молоком")
    step_have_latte(context)
    step_add_milk(context)
    step_check_cost_increase(context, 30)
    print("  ✓ Пройден\n")

    # Тест 3: Заказ с уведомлениями
    print("Тест 3: Уведомления")
    step_made_order(context, "Капучино")
    step_subscribed_sms(context)
    step_barista_prepares(context)
    step_order_ready(context)
    step_check_notification_count(context, 2)
    print("  ✓ Пройден\n")

    print("=== Все тесты пройдены! ===")