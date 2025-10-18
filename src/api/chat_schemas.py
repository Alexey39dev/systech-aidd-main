"""Pydantic схемы для Chat API."""

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class ChatMode(str, Enum):
    """Режимы работы чата."""

    NORMAL = "normal"
    ADMIN = "admin"


class ChatMessageRequest(BaseModel):
    """Запрос на отправку сообщения в чат."""

    message: str = Field(..., min_length=1, max_length=4000, description="Текст сообщения")
    mode: ChatMode = Field(default=ChatMode.NORMAL, description="Режим работы чата")
    session_id: str | None = Field(default=None, description="ID сессии пользователя")

    class Config:
        """Конфигурация модели."""

        json_schema_extra = {
            "example": {
                "message": "Привет! Как дела?",
                "mode": "normal",
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
            }
        }


class ChatMessageResponse(BaseModel):
    """Ответ с сообщением от ассистента."""

    message: str = Field(..., description="Ответ ассистента")
    mode: ChatMode = Field(..., description="Режим, в котором был обработан запрос")
    sql_query: str | None = Field(default=None, description="SQL запрос (только для admin режима)")
    metadata: dict[str, str | int] | None = Field(
        default=None, description="Дополнительные метаданные ответа"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Время ответа")

    class Config:
        """Конфигурация модели."""

        json_schema_extra = {
            "example": {
                "message": "Привет! У меня все хорошо, спасибо! Как дела у вас?",
                "mode": "normal",
                "sql_query": None,
                "metadata": {"tokens_used": 45, "response_time_ms": 1200},
                "timestamp": "2025-01-17T10:30:00Z",
            }
        }


class ChatMessage(BaseModel):
    """Сообщение в истории диалога."""

    role: Literal["user", "assistant"] = Field(..., description="Роль отправителя")
    content: str = Field(..., description="Содержимое сообщения")
    timestamp: datetime = Field(..., description="Время отправки")
    mode: ChatMode | None = Field(default=None, description="Режим (только для assistant)")

    class Config:
        """Конфигурация модели."""

        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "Сколько пользователей зарегистрировано?",
                "timestamp": "2025-01-17T10:30:00Z",
                "mode": None,
            }
        }


class ChatHistoryResponse(BaseModel):
    """Ответ с историей диалога."""

    messages: list[ChatMessage] = Field(..., description="Список сообщений")
    session_id: str = Field(..., description="ID сессии")
    total_messages: int = Field(..., description="Общее количество сообщений")
    last_activity: datetime | None = Field(default=None, description="Время последней активности")

    class Config:
        """Конфигурация модели."""

        json_schema_extra = {
            "example": {
                "messages": [
                    {
                        "role": "user",
                        "content": "Привет!",
                        "timestamp": "2025-01-17T10:30:00Z",
                        "mode": None,
                    },
                    {
                        "role": "assistant",
                        "content": "Привет! Как дела?",
                        "timestamp": "2025-01-17T10:30:05Z",
                        "mode": "normal",
                    },
                ],
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "total_messages": 2,
                "last_activity": "2025-01-17T10:30:05Z",
            }
        }


class ChatSession(BaseModel):
    """Информация о сессии чата."""

    session_id: str = Field(..., description="ID сессии")
    user_id: int = Field(..., description="ID пользователя")
    created_at: datetime = Field(..., description="Время создания сессии")
    last_activity: datetime | None = Field(default=None, description="Время последней активности")
    message_count: int = Field(default=0, description="Количество сообщений в сессии")

    class Config:
        """Конфигурация модели."""

        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": 42,
                "created_at": "2025-01-17T10:00:00Z",
                "last_activity": "2025-01-17T10:30:05Z",
                "message_count": 5,
            }
        }
