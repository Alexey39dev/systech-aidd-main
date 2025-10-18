"""Интерфейс для сборщиков статистики."""

from abc import ABC, abstractmethod

from .schemas import StatsResponse


class StatCollector(ABC):
    """Абстрактный базовый класс для сборщиков статистики диалогов."""

    @abstractmethod
    async def get_stats(self, period: str) -> StatsResponse:
        """
        Получить статистику за указанный период.

        Args:
            period: Период для статистики ("day", "week", "month")

        Returns:
            StatsResponse с полной статистикой

        Raises:
            ValueError: Если период некорректен
        """
        pass

