"""Объединение всех паттернов в единую систему"""

from coffee import Coffee
from factory import SimpleCoffeeFactory
from decorator import (
    MilkDecorator, SugarDecorator, SyrupDecorator,
    WhippedCreamDecorator, ExtraShotDecorator
)
from observer import (
    Order, OrderStatus, CustomerNotifier,
    BaristaDisplay, OrderLogger, KitchenPrinter
)


class CoffeeShop:
    """Кофейня - объединяет все паттерны"""

    def __init__(self, name: str):
        self.name = name
        self.orders: list = []

        # Создаём наблюдателей (Observer)
        self.barista_display = BaristaDisplay()
        self.logger = OrderLogger()
        self.printer = KitchenPrinter()

    def create_order(self, customer_name: str, coffee_type: str,
                     additions: list = None, notify_method: str = "sms") -> Order:
        """Создаёт заказ используя Factory и Decorator"""

        # Factory Method - создаём базовый кофе
        coffee = SimpleCoffeeFactory.create(coffee_type)

        # Decorator - добавляем добавки
        if additions:
            coffee = self._apply_additions(coffee, additions)

        # Observer - создаём заказ с наблюдателями
        order = Order(coffee.get_description(), customer_name)
        order.attach(CustomerNotifier(notify_method))
        order.attach(self.barista_display)
        order.attach(self.logger)
        order.attach(self.printer)

        self.orders.append(order)

        # Устанавливаем начальный статус
        order.set_status(OrderStatus.CREATED,
                         f"{coffee.get_description()} - {coffee.get_cost()} руб.")

        return order

    def _apply_additions(self, coffee: Coffee, additions: list) -> Coffee:
        """Применяет добавки к кофе (Decorator)"""

        decorators = {
            'milk': MilkDecorator,
            'sugar': SugarDecorator,
            'whipped_cream': WhippedCreamDecorator,
            'extra_shot': ExtraShotDecorator
        }

        for addition in additions:
            if addition in decorators:
                coffee = decorators[addition](coffee)
            elif addition.startswith('syrup_'):
                syrup_type = addition.replace('syrup_', '')
                coffee = SyrupDecorator(coffee, syrup_type)

        return coffee

    def process_order(self, order: Order) -> None:
        """Обрабатывает заказ (меняет статусы)"""
        order.set_status(OrderStatus.PREPARING)
        order.set_status(OrderStatus.READY, "Заберите ваш заказ!")

    def complete_order(self, order: Order) -> None:
        """Завершает заказ"""
        order.set_status(OrderStatus.DELIVERED)


if __name__ == '__main__':
    print("=" * 60)
    print("      КОФЕЙНЯ 'PYTHON COFFEE'")
    print("=" * 60)

    shop = CoffeeShop("Python Coffee")

    # Заказ 1: Простой эспрессо
    print("\n>>> Заказ 1: Простой эспрессо")
    order1 = shop.create_order("Алексей", "espresso")
    shop.process_order(order1)
    shop.complete_order(order1)

    # Заказ 2: Латте с добавками
    print("\n>>> Заказ 2: Латте с добавками")
    order2 = shop.create_order(
        "Мария",
        "latte",
        additions=['milk', 'syrup_caramel', 'whipped_cream'],
        notify_method="push"
    )
    shop.process_order(order2)

    print("\n" + "=" * 60)
    print(f"Заказов в очереди: {shop.barista_display.orders_queue}")
    print(f"Всего записей в логе: {len(shop.logger.logs)}")
    print("=" * 60)