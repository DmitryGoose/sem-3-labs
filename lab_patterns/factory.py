"""
Паттерн Factory Method (Фабричный метод)

Определяет интерфейс для создания объекта, но позволяет подклассам
решать, какой класс инстанцировать.
"""

from abc import ABC, abstractmethod
from coffee import Coffee, Espresso, Americano, Cappuccino, Latte


class CoffeeFactory(ABC):
    """Абстрактная фабрика кофе"""

    @abstractmethod
    def create_coffee(self) -> Coffee:
        """Фабричный метод для создания кофе"""
        pass

    def order_coffee(self) -> Coffee:
        """Шаблонный метод для заказа кофе"""
        coffee = self.create_coffee()
        print(f"Готовим: {coffee.get_description()}")
        return coffee


class EspressoFactory(CoffeeFactory):
    """Фабрика для создания эспрессо"""

    def create_coffee(self) -> Coffee:
        return Espresso()


class AmericanoFactory(CoffeeFactory):
    """Фабрика для создания американо"""

    def create_coffee(self) -> Coffee:
        return Americano()


class CappuccinoFactory(CoffeeFactory):
    """Фабрика для создания капучино"""

    def create_coffee(self) -> Coffee:
        return Cappuccino()


class LatteFactory(CoffeeFactory):
    """Фабрика для создания латте"""

    def create_coffee(self) -> Coffee:
        return Latte()


class SimpleCoffeeFactory:
    """Простая фабрика кофе (альтернативная реализация)"""

    _factories = {
        'espresso': EspressoFactory,
        'americano': AmericanoFactory,
        'cappuccino': CappuccinoFactory,
        'latte': LatteFactory
    }

    @classmethod
    def create(cls, coffee_type: str) -> Coffee:
        """Создает кофе по типу"""
        coffee_type = coffee_type.lower()

        if coffee_type not in cls._factories:
            raise ValueError(f"Неизвестный тип кофе: {coffee_type}")

        factory = cls._factories[coffee_type]()
        return factory.create_coffee()

    @classmethod
    def get_available_types(cls) -> list:
        """Возвращает список доступных типов кофе"""
        return list(cls._factories.keys())


if __name__ == '__main__':
    print("=== Демонстрация Factory Method ===\n")

    # Использование конкретных фабрик
    factories = [EspressoFactory(), AmericanoFactory(), CappuccinoFactory()]

    for factory in factories:
        coffee = factory.order_coffee()
        print(f"  Стоимость: {coffee.get_cost()} руб.\n")

    print("=== Использование SimpleCoffeeFactory ===\n")
    print(f"Доступные типы: {SimpleCoffeeFactory.get_available_types()}\n")

    for coffee_type in SimpleCoffeeFactory.get_available_types():
        coffee = SimpleCoffeeFactory.create(coffee_type)
        print(coffee)