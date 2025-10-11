"""Типы данных для приложения."""

from typing import Literal, TypedDict

# Literal типы для ролей в диалоге
MessageRole = Literal["user", "assistant", "system"]


class Message(TypedDict):
    """Типизированное сообщение в диалоге.

    Используется для строгой типизации истории диалога
    вместо общего dict[str, str].
    """

    role: MessageRole
    content: str
