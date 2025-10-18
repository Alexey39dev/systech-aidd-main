"""Pydantic схемы для API статистики."""

from typing import Literal

from pydantic import BaseModel, Field


class MetricCard(BaseModel):
    """Карточка с метрикой для дашборда."""

    label: str = Field(..., description="Название метрики")
    value: str | int | float = Field(..., description="Значение метрики")
    change: str = Field(..., description="Изменение относительно предыдущего периода (например, '+12.5%')")
    trend: Literal["up", "down", "neutral"] = Field(..., description="Направление тренда")

    class Config:
        """Конфигурация модели."""

        json_schema_extra = {
            "example": {
                "label": "Total Dialogs",
                "value": 1247,
                "change": "+12.5%",
                "trend": "up",
            }
        }


class TimelinePoint(BaseModel):
    """Точка данных для графика активности."""

    timestamp: str = Field(..., description="Временная метка в ISO формате")
    value: int = Field(..., ge=0, description="Количество сообщений")

    class Config:
        """Конфигурация модели."""

        json_schema_extra = {
            "example": {
                "timestamp": "2025-10-17T14:00:00Z",
                "value": 42,
            }
        }


class RecentDialog(BaseModel):
    """Информация о недавнем диалоге."""

    user_id: int = Field(..., gt=0, description="ID пользователя")
    username: str = Field(..., min_length=1, description="Имя пользователя")
    messages_count: int = Field(..., ge=0, description="Количество сообщений в диалоге")
    last_activity: str = Field(..., description="Время последней активности в ISO формате")

    class Config:
        """Конфигурация модели."""

        json_schema_extra = {
            "example": {
                "user_id": 42,
                "username": "alice_wonder",
                "messages_count": 15,
                "last_activity": "2025-10-17T14:23:15Z",
            }
        }


class TopUser(BaseModel):
    """Информация о топ пользователе."""

    user_id: int = Field(..., gt=0, description="ID пользователя")
    username: str = Field(..., min_length=1, description="Имя пользователя")
    messages_count: int = Field(..., ge=0, description="Общее количество сообщений")
    dialogs_count: int = Field(..., ge=0, description="Количество диалогов")

    class Config:
        """Конфигурация модели."""

        json_schema_extra = {
            "example": {
                "user_id": 7,
                "username": "power_user_123",
                "messages_count": 156,
                "dialogs_count": 12,
            }
        }


class StatsResponse(BaseModel):
    """Ответ API со статистикой диалогов."""

    period: Literal["day", "week", "month"] = Field(..., description="Период статистики")
    metrics: list[MetricCard] = Field(..., min_length=4, max_length=4, description="4 карточки с метриками")
    timeline: list[TimelinePoint] = Field(..., description="Данные для графика активности")
    recent_dialogs: list[RecentDialog] = Field(
        ..., max_length=10, description="Список последних диалогов (до 10)"
    )
    top_users: list[TopUser] = Field(..., max_length=10, description="Топ пользователей (до 10)")

    class Config:
        """Конфигурация модели."""

        json_schema_extra = {
            "example": {
                "period": "day",
                "metrics": [
                    {
                        "label": "Total Dialogs",
                        "value": 1247,
                        "change": "+12.5%",
                        "trend": "up",
                    },
                    {
                        "label": "Active Users",
                        "value": 58,
                        "change": "+5.2%",
                        "trend": "up",
                    },
                    {
                        "label": "Avg Dialog Length",
                        "value": 8.3,
                        "change": "-2.1%",
                        "trend": "down",
                    },
                    {
                        "label": "Messages Today",
                        "value": 342,
                        "change": "+18.7%",
                        "trend": "up",
                    },
                ],
                "timeline": [
                    {"timestamp": "2025-10-17T00:00:00Z", "value": 12},
                    {"timestamp": "2025-10-17T01:00:00Z", "value": 8},
                ],
                "recent_dialogs": [
                    {
                        "user_id": 42,
                        "username": "alice_wonder",
                        "messages_count": 15,
                        "last_activity": "2025-10-17T14:23:15Z",
                    }
                ],
                "top_users": [
                    {
                        "user_id": 7,
                        "username": "power_user_123",
                        "messages_count": 156,
                        "dialogs_count": 12,
                    }
                ],
            }
        }

