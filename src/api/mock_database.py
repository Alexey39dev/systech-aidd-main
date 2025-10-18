"""Mock DatabaseClient для работы без реальной БД."""

from datetime import datetime
from typing import Final

from ..logger import get_logger
from ..types import MessageDBDict, MessageRole


class MockDatabaseClient:
    """Mock-клиент для работы с БД в режиме тестирования."""

    def __init__(
        self,
        database_url: str,
        pool_min_size: int = 5,
        pool_max_size: int = 20,
    ):
        """
        Инициализация mock-клиента БД.

        Args:
            database_url: URL подключения к PostgreSQL (игнорируется)
            pool_min_size: Минимальный размер пула соединений (игнорируется)
            pool_max_size: Максимальный размер пула соединений (игнорируется)
        """
        self.database_url = database_url
        self.pool_min_size = pool_min_size
        self.pool_max_size = pool_max_size
        self.logger = get_logger("mock_database")
        
        # In-memory хранилище
        self._messages: list[MessageDBDict] = []
        self._users: dict[str, int] = {}  # username -> user_id
        self._next_user_id: int = 1
        self._next_message_id: int = 1

    async def connect(self) -> None:
        """Mock-подключение к БД."""
        self.logger.info("Mock database client initialized")

    async def close(self) -> None:
        """Mock-закрытие соединения."""
        self.logger.info("Mock database client closed")

    def _check_pool(self) -> None:
        """Проверка инициализации (всегда проходит для mock)."""
        pass

    async def add_message(
        self, role: MessageRole, content: str, user_id: int
    ) -> tuple[int, datetime]:
        """
        Добавить сообщение в mock-БД.

        Args:
            role: Роль отправителя (user/assistant/system)
            content: Содержимое сообщения
            user_id: ID пользователя

        Returns:
            Tuple с (id сообщения, timestamp создания)
        """
        message_id = self._next_message_id
        self._next_message_id += 1
        now = datetime.utcnow()

        message: MessageDBDict = {
            "id": message_id,
            "role": role,
            "content": content,
            "created_at": now.isoformat(),
            "length": len(content),
            "deleted_at": None,
        }

        self._messages.append(message)

        self.logger.debug(
            "Сообщение добавлено в mock-БД",
            message_id=message_id,
            role=role,
            length=len(content),
            user_id=user_id,
        )

        return message_id, now

    async def get_messages(self) -> list[MessageDBDict]:
        """
        Получить все активные (не удаленные) сообщения.

        Returns:
            Список сообщений с метаданными
        """
        active_messages = [msg for msg in self._messages if msg["deleted_at"] is None]
        
        self.logger.debug("Получены сообщения из mock-БД", count=len(active_messages))
        return active_messages

    async def soft_delete_message(self, message_id: int) -> None:
        """
        Мягкое удаление сообщения (установка deleted_at).

        Args:
            message_id: ID сообщения для удаления
        """
        for message in self._messages:
            if message["id"] == message_id:
                message["deleted_at"] = datetime.utcnow().isoformat()
                break

        self.logger.debug("Сообщение помечено как удаленное", message_id=message_id)

    async def clear_all_messages(self) -> int:
        """
        Мягкое удаление всех активных сообщений.

        Returns:
            Количество удаленных сообщений
        """
        deleted_count = 0
        now = datetime.utcnow().isoformat()
        
        for message in self._messages:
            if message["deleted_at"] is None:
                message["deleted_at"] = now
                deleted_count += 1

        self.logger.info("Все сообщения помечены как удаленные", count=deleted_count)
        return deleted_count

    async def get_or_create_user(self, username: str) -> tuple[int, datetime]:
        """
        Получить или создать пользователя по username.

        Args:
            username: Имя пользователя

        Returns:
            Tuple с (id пользователя, timestamp создания/обновления)
        """
        now = datetime.utcnow()

        if username in self._users:
            # Пользователь найден
            user_id = self._users[username]
            self.logger.debug(
                "Пользователь найден",
                user_id=user_id,
                username=username,
            )
            return user_id, now
        else:
            # Создаем нового пользователя
            user_id = self._next_user_id
            self._next_user_id += 1
            self._users[username] = user_id

            self.logger.debug(
                "Создан новый пользователь",
                user_id=user_id,
                username=username,
            )

            return user_id, now

    async def soft_delete_user(self, user_id: int) -> None:
        """
        Мягкое удаление пользователя (заглушка для mock).

        Args:
            user_id: ID пользователя для удаления
        """
        # В mock-режиме просто логируем
        self.logger.debug("Пользователь помечен как удаленный (mock)", user_id=user_id)

    def __repr__(self) -> str:
        """Строковое представление mock-клиента БД."""
        return (
            f"MockDatabaseClient("
            f"messages={len(self._messages)}, "
            f"users={len(self._users)}"
            f")"
        )
