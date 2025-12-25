"""Базовые классы для системы заказа кофе"""

from abc import ABC, abstractmethod


class Coffee(ABC):
    """Абстрактный базовый класс для кофе"""

    @abstractmethod
    def get_description(self) -> str:
        """Возвращает описание кофе"""
        pass

    @abstractmethod
    def get_cost(self) -> float:
        """Возвращает стоимость кофе"""
        pass

    def __str__(self) -> str:
        return f"{self.get_description()}: {self.get_cost()} руб."


class Espresso(Coffee):
    """Эспрессо"""

    def get_description(self) -> str:
        return "Эспрессо"

    def get_cost(self) -> float:
        return 150.0


class Americano(Coffee):
    """Американо"""

    def get_description(self) -> str:
        return "Американо"

    def get_cost(self) -> float:
        return 180.0


class Cappuccino(Coffee):
    """Капучино"""

    def get_description(self) -> str:
        return "Капучино"

    def get_cost(self) -> float:
        return 220.0


class Latte(Coffee):
    """Латте"""

    def get_description(self) -> str:
        return "Латте"

    def get_cost(self) -> float:
        return 250.0


if __name__ == '__main__':
    # Демонстрация базовых классов
    coffees = [Espresso(), Americano(), Cappuccino(), Latte()]

    print("=== Меню кофе ===")
    for coffee in coffees:
        print(coffee)