"""
Паттерн Decorator (Декоратор)

Динамически добавляет объекту новые обязанности.
Является гибкой альтернативой наследованию.
"""

from abc import ABC, abstractmethod
from coffee import Coffee, Espresso, Americano, Cappuccino, Latte


class CoffeeDecorator(Coffee, ABC):
    """Абстрактный декоратор для кофе"""

    def __init__(self, coffee: Coffee):
        self._coffee = coffee

    @abstractmethod
    def get_description(self) -> str:
        pass

    @abstractmethod
    def get_cost(self) -> float:
        pass


class MilkDecorator(CoffeeDecorator):
    """Добавка: молоко"""

    def get_description(self) -> str:
        return f"{self._coffee.get_description()} + молоко"

    def get_cost(self) -> float:
        return self._coffee.get_cost() + 30.0


class SugarDecorator(CoffeeDecorator):
    """Добавка: сахар"""

    def get_description(self) -> str:
        return f"{self._coffee.get_description()} + сахар"

    def get_cost(self) -> float:
        return self._coffee.get_cost() + 10.0


class SyrupDecorator(CoffeeDecorator):
    """Добавка: сироп"""

    SYRUPS = {
        'vanilla': ('ванильный сироп', 50.0),
        'caramel': ('карамельный сироп', 50.0),
        'hazelnut': ('ореховый сироп', 55.0),
        'chocolate': ('шоколадный сироп', 60.0)
    }

    def __init__(self, coffee: Coffee, syrup_type: str = 'vanilla'):
        super().__init__(coffee)
        if syrup_type not in self.SYRUPS:
            raise ValueError(f"Неизвестный тип сиропа: {syrup_type}")
        self._syrup_type = syrup_type

    def get_description(self) -> str:
        syrup_name = self.SYRUPS[self._syrup_type][0]
        return f"{self._coffee.get_description()} + {syrup_name}"

    def get_cost(self) -> float:
        syrup_cost = self.SYRUPS[self._syrup_type][1]
        return self._coffee.get_cost() + syrup_cost


class WhippedCreamDecorator(CoffeeDecorator):
    """Добавка: взбитые сливки"""

    def get_description(self) -> str:
        return f"{self._coffee.get_description()} + взбитые сливки"

    def get_cost(self) -> float:
        return self._coffee.get_cost() + 40.0


class ExtraShotDecorator(CoffeeDecorator):
    """Добавка: дополнительная порция эспрессо"""

    def get_description(self) -> str:
        return f"{self._coffee.get_description()} + доп. эспрессо"

    def get_cost(self) -> float:
        return self._coffee.get_cost() + 70.0


if __name__ == '__main__':
    print("=== Демонстрация паттерна Decorator ===\n")

    # Простой эспрессо
    coffee = Espresso()
    print(f"Базовый: {coffee}")

    # Эспрессо с молоком
    coffee_with_milk = MilkDecorator(Espresso())
    print(f"С молоком: {coffee_with_milk}")

    # Латте с сиропом и сливками
    fancy_latte = WhippedCreamDecorator(
        SyrupDecorator(
            Latte(),
            'caramel'
        )
    )
    print(f"Латте с добавками: {fancy_latte}")

    # Американо "полный фарш"
    super_americano = ExtraShotDecorator(
        WhippedCreamDecorator(
            SyrupDecorator(
                MilkDecorator(
                    SugarDecorator(
                        Americano()
                    )
                ),
                'chocolate'
            )
        )
    )
    print(f"\nСупер-американо: {super_americano}")