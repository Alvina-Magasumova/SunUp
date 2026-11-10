from abc import ABC, abstractmethod


class NotificationChannel(ABC):
    """
    Базовый интерфейс канала доставки
    Каждый канал (email, telegram, max) реализует метод send()
    """

    @abstractmethod
    def send(self, user, message: str) -> bool:
        """
        Отправить сообщение пользователю
        Возвращает True при успехе, False при ошибке
        """
        raise NotImplementedError