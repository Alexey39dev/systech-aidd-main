"""Управление диалогами и историей сообщений."""

from .database import DatabaseClient
from .logger import get_logger
from .types import Message, MessageRole


class DialogManager:
    """Класс для управления диалогами и историей сообщений через БД."""

    def __init__(self, db_client: DatabaseClient, user_id: int, max_history: int = 10):
        """
        Инициализация менеджера диалогов.

        Args:
            db_client: Клиент для работы с БД
            user_id: ID пользователя
            max_history: Максимальное количество пар сообщений в истории
        """
        self.db_client = db_client
        self.user_id = user_id
        self.max_history = max_history
        self.logger = get_logger("dialog_manager")

    async def add_message(self, role: MessageRole, content: str) -> None:
        """
        Добавить сообщение в историю диалога (сохраняет в БД).

        Args:
            role: Роль отправителя (user/assistant/system)
            content: Содержимое сообщения
        """
        if not content.strip():
            self.logger.warning("Попытка добавить пустое сообщение")
            return

        # Сохраняем в БД
        message_id, created_at = await self.db_client.add_message(role, content, self.user_id)

        # Обрезаем старые сообщения если превышен лимит
        await self._trim_history()

        self.logger.debug(
            "Сообщение добавлено в БД",
            message_id=message_id,
            role=role,
            content_length=len(content),
        )

    async def add_user_message(self, content: str) -> None:
        """
        Добавить сообщение пользователя в историю.

        Args:
            content: Содержимое сообщения
        """
        await self.add_message("user", content)

    async def add_assistant_message(self, content: str) -> None:
        """
        Добавить сообщение ассистента в историю.

        Args:
            content: Содержимое сообщения
        """
        await self.add_message("assistant", content)

    async def get_history(self) -> list[Message]:
        """
        Получить историю диалога из БД.

        Returns:
            Список типизированных сообщений (только role и content для LLM API)
        """
        messages_db = await self.db_client.get_messages()

        # Конвертируем MessageDBDict в Message (только role и content)
        history: list[Message] = []
        for msg in messages_db:
            history.append({"role": msg["role"], "content": msg["content"]})

        return history

    async def clear_history(self) -> None:
        """Очистить историю диалога (soft delete в БД)."""
        deleted_count = await self.db_client.clear_all_messages()
        self.logger.info("История диалога очищена", deleted_count=deleted_count)

    async def get_history_length(self) -> int:
        """
        Получить текущую длину истории из БД.

        Returns:
            Количество активных сообщений в истории
        """
        messages = await self.db_client.get_messages()
        return len(messages)

    async def get_conversation_summary(self) -> dict[str, int]:
        """
        Получить сводную статистику по диалогу из БД.

        Returns:
            Словарь со статистикой диалога
        """
        messages = await self.db_client.get_messages()

        user_messages = sum(1 for msg in messages if msg["role"] == "user")
        assistant_messages = sum(1 for msg in messages if msg["role"] == "assistant")

        return {
            "total_messages": len(messages),
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "max_history": self.max_history,
        }

    async def _trim_history(self) -> None:
        """
        Обрезать историю до максимальной длины через soft delete.

        Удаляет старые сообщения если превышен max_history * 2.
        """
        messages = await self.db_client.get_messages()
        max_messages = self.max_history * 2  # Пары: user + assistant

        if len(messages) > max_messages:
            # Удаляем старые сообщения (soft delete)
            messages_to_delete = messages[: len(messages) - max_messages]
            for msg in messages_to_delete:
                await self.db_client.soft_delete_message(msg["id"])

            self.logger.debug(
                "История обрезана",
                removed_messages=len(messages_to_delete),
                current_length=max_messages,
            )

    async def __len__(self) -> int:
        """Получить длину истории через len()."""
        return await self.get_history_length()

    def __repr__(self) -> str:
        """Строковое представление менеджера диалогов."""
        return f"DialogManager(user_id={self.user_id}, max_history={self.max_history}, db_client={self.db_client})"
