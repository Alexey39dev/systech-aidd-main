"""Управление диалогами и историей сообщений."""

from .logger import get_logger
from .types import Message, MessageRole


class DialogManager:
    """Класс для управления диалогами и историей сообщений."""

    def __init__(self, max_history: int = 10):
        """
        Инициализация менеджера диалогов.

        Args:
            max_history: Максимальное количество пар сообщений в истории
        """
        self.max_history = max_history
        self.history: list[Message] = []
        self.logger = get_logger("dialog_manager")

    def add_message(self, role: MessageRole, content: str) -> None:
        """
        Добавить сообщение в историю диалога.

        Args:
            role: Роль отправителя (user/assistant/system)
            content: Содержимое сообщения
        """
        if not content.strip():
            self.logger.warning("Попытка добавить пустое сообщение")
            return

        self.history.append({"role": role, "content": content})
        self._trim_history()

        self.logger.debug(
            "Сообщение добавлено в историю",
            role=role,
            content_length=len(content),
            history_length=len(self.history),
        )

    def add_user_message(self, content: str) -> None:
        """
        Добавить сообщение пользователя в историю.

        Args:
            content: Содержимое сообщения
        """
        self.add_message("user", content)

    def add_assistant_message(self, content: str) -> None:
        """
        Добавить сообщение ассистента в историю.

        Args:
            content: Содержимое сообщения
        """
        self.add_message("assistant", content)

    def get_history(self) -> list[Message]:
        """
        Получить историю диалога.

        Returns:
            Список типизированных сообщений
        """
        return self.history.copy()

    def clear_history(self) -> None:
        """Очистить историю диалога."""
        history_length = len(self.history)
        self.history.clear()
        self.logger.info("История диалога очищена", previous_length=history_length)

    def get_history_length(self) -> int:
        """
        Получить текущую длину истории.

        Returns:
            Количество сообщений в истории
        """
        return len(self.history)

    def get_conversation_summary(self) -> dict[str, int]:
        """
        Получить сводную статистику по диалогу.

        Returns:
            Словарь со статистикой диалога
        """
        user_messages = sum(1 for msg in self.history if msg["role"] == "user")
        assistant_messages = sum(1 for msg in self.history if msg["role"] == "assistant")

        return {
            "total_messages": len(self.history),
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "max_history": self.max_history,
        }

    def _trim_history(self) -> None:
        """
        Обрезать историю до максимальной длины.

        Сохраняет последние max_history пар сообщений (user + assistant).
        """
        max_messages = self.max_history * 2  # Пары: user + assistant

        if len(self.history) > max_messages:
            removed_count = len(self.history) - max_messages
            self.history = self.history[-max_messages:]
            self.logger.debug(
                "История обрезана", removed_messages=removed_count, current_length=len(self.history)
            )

    def __len__(self) -> int:
        """Получить длину истории через len()."""
        return len(self.history)

    def __repr__(self) -> str:
        """Строковое представление менеджера диалогов."""
        stats = self.get_conversation_summary()
        return f"DialogManager(messages={stats['total_messages']}, max_history={self.max_history})"
