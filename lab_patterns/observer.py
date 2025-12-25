"""
Паттерн Observer (Наблюдатель)

Определяет зависимость "один ко многим" между объектами так,
что при изменении состояния одного объекта все зависящие от него
объекты уведомляются и обновляются автоматически.
"""

from abc import ABC, abstractmethod
from typing import List
from enum import Enum
from datetime import datetime


class OrderStatus(Enum):
    """Статусы заказа"""
    CREATED = "создан"
    PREPARING = "готовится"
    READY = "готов"
    DELIVERED = "выдан"
    CANCELLED = "отменён"


class OrderObserver(ABC):
    """Абстрактный наблюдатель за заказом"""

    @abstractmethod
    def update(self, order_id: int, status: OrderStatus, message: str = "") -> None:
        """Вызывается при изменении статуса заказа"""
        pass


class Order:
    """Заказ кофе (Subject/Observable)"""

    _order_counter = 0

    def __init__(self, coffee_description: str, customer_name: str):
        Order._order_counter += 1
        self._id = Order._order_counter
        self._coffee = coffee_description
        self._customer = customer_name
        self._status = OrderStatus.CREATED
        self._observers: List[OrderObserver] = []

    @property
    def id(self) -> int:
        return self._id

    @property
    def status(self) -> OrderStatus:
        return self._status

    @property
    def coffee(self) -> str:
        return self._coffee

    @property
    def customer(self) -> str:
        return self._customer

    def attach(self, observer: OrderObserver) -> None:
        """Добавляет наблюдателя"""
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: OrderObserver) -> None:
        """Удаляет наблюдателя"""
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, message: str = "") -> None:
        """Уведомляет всех наблюдателей"""
        for observer in self._observers:
            observer.update(self._id, self._status, message)

    def set_status(self, status: OrderStatus, message: str = "") -> None:
        """Изменяет статус и уведомляет наблюдателей"""
        self._status = status
        self.notify(message)

    def __str__(self) -> str:
        return f"Заказ #{self._id}: {self._coffee} для {self._customer} [{self._status.value}]"


class CustomerNotifier(OrderObserver):
    """Уведомляет клиента о статусе заказа"""

    def __init__(self, notification_method: str = "sms"):
        self._method = notification_method
        self.notifications: List[str] = []  # Для тестирования

    def update(self, order_id: int, status: OrderStatus, message: str = "") -> None:
        notification = f"[{self._method.upper()}] Заказ #{order_id}: {status.value}"
        if message:
            notification += f" - {message}"

        self.notifications.append(notification)
        print(notification)


class BaristaDisplay(OrderObserver):
    """Отображает заказы на экране бариста"""

    def __init__(self):
        self.orders_queue: List[str] = []

    def update(self, order_id: int, status: OrderStatus, message: str = "") -> None:
        display_message = f"[ДИСПЛЕЙ] Заказ #{order_id} -> {status.value}"

        if status == OrderStatus.CREATED:
            self.orders_queue.append(f"Заказ #{order_id}")
            display_message += " (добавлен в очередь)"
        elif status in [OrderStatus.READY, OrderStatus.DELIVERED, OrderStatus.CANCELLED]:
            order_str = f"Заказ #{order_id}"
            if order_str in self.orders_queue:
                self.orders_queue.remove(order_str)
                display_message += " (убран из очереди)"

        print(display_message)


class OrderLogger(OrderObserver):
    def __init__(self):
        self.logs = []

    def update(self, order_id: int, status: OrderStatus, message: str = "") -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] Заказ #{order_id}: статус изменён на '{status.value}'"
        if message:
            log_entry += f" ({message})"

        self.logs.append(log_entry)
        print(f"[LOG] {log_entry}")


class KitchenPrinter(OrderObserver):
    """Печатает чек на кухне при создании заказа"""

    def __init__(self):
        self.printed_orders: List[int] = []

    def update(self, order_id: int, status: OrderStatus, message: str = "") -> None:
        if status == OrderStatus.CREATED:
            self.printed_orders.append(order_id)
            print(f"[ПРИНТЕР] === Печать чека для заказа #{order_id} ===")


if __name__ == '__main__':
    print("=== Демонстрация паттерна Observer ===\n")

    # Создаём наблюдателей
    customer_sms = CustomerNotifier("sms")
    customer_push = CustomerNotifier("push")
    barista_display = BaristaDisplay()
    logger = OrderLogger()
    printer = KitchenPrinter()

    # Создаём заказ
    order = Order("Капучино с карамельным сиропом", "Иван")

    # Подписываем наблюдателей
    order.attach(customer_sms)
    order.attach(barista_display)
    order.attach(logger)
    order.attach(printer)

    print(f"\n{order}\n")

    # Меняем статусы
    print("--- Заказ создан ---")
    order.set_status(OrderStatus.CREATED, "Заказ принят")

    print("\n--- Начинаем готовить ---")
    order.set_status(OrderStatus.PREPARING, "Бариста Мария готовит ваш напиток")

    print("\n--- Заказ готов ---")
    order.set_status(OrderStatus.READY, "Заберите на стойке")

    print("\n--- Заказ выдан ---")
    order.set_status(OrderStatus.DELIVERED)

    print(f"\n\nОчередь на дисплее: {barista_display.orders_queue}")
    print(f"Логов записано: {len(logger.logs)}")