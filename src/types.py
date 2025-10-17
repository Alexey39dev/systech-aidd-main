"""Типы данных для приложения."""

from typing import Literal, TypedDict

# Literal типы для ролей в диалоге
MessageRole = Literal["user", "assistant", "system"]


class Message(TypedDict):
    """Типизированное сообщение в диалоге (для API LLM и in-memory использования).

    Используется для строгой типизации истории диалога
    вместо общего dict[str, str].
    """

    role: MessageRole
    content: str


class MessageDict(TypedDict):
    """Сообщение с метаданными (для возврата из БД в приложение)."""

    role: MessageRole
    content: str
    created_at: str  # ISO format timestamp
    length: int


class MessageDBDict(TypedDict):
    """Полная запись сообщения из БД со всеми полями."""

    id: int
    role: MessageRole
    content: str
    created_at: str  # ISO format timestamp
    length: int
    deleted_at: str | None  # ISO format timestamp or None


class UserDBDict(TypedDict):
    """Полная запись пользователя из БД со всеми полями."""

    id: int
    username: str
    created_at: str  # ISO format timestamp
    updated_at: str  # ISO format timestamp
    deleted_at: str | None  # ISO format timestamp or None
