"""Клиент для работы с базой данных PostgreSQL."""

from datetime import datetime

import asyncpg  # type: ignore[import-untyped]

from .logger import get_logger
from .types import MessageDBDict, MessageRole


class DatabaseClient:
    """Клиент для работы с PostgreSQL через asyncpg."""

    def __init__(
        self,
        database_url: str,
        pool_min_size: int = 5,
        pool_max_size: int = 20,
    ):
        """
        Инициализация клиента БД.

        Args:
            database_url: URL подключения к PostgreSQL
            pool_min_size: Минимальный размер пула соединений
            pool_max_size: Максимальный размер пула соединений
        """
        self.database_url = database_url
        self.pool_min_size = pool_min_size
        self.pool_max_size = pool_max_size
        self._pool: asyncpg.Pool | None = None
        self.logger = get_logger("database")

    async def connect(self) -> None:
        """Создать пул соединений с БД."""
        self.logger.info(
            "Создание пула соединений к БД",
            min_size=self.pool_min_size,
            max_size=self.pool_max_size,
        )

        self._pool = await asyncpg.create_pool(
            self.database_url,
            min_size=self.pool_min_size,
            max_size=self.pool_max_size,
        )

        self.logger.info("Пул соединений создан успешно")

    async def close(self) -> None:
        """Закрыть пул соединений."""
        if self._pool is not None:
            self.logger.info("Закрытие пула соединений")
            await self._pool.close()
            self._pool = None
            self.logger.info("Пул соединений закрыт")

    def _check_pool(self) -> None:
        """Проверить что пул инициализирован."""
        if self._pool is None:
            raise RuntimeError("Database pool not initialized. Call connect() first.")

    async def add_message(
        self, role: MessageRole, content: str, user_id: int
    ) -> tuple[int, datetime]:
        """
        Добавить сообщение в БД.

        Args:
            role: Роль отправителя (user/assistant/system)
            content: Содержимое сообщения
            user_id: ID пользователя

        Returns:
            Tuple с (id сообщения, timestamp создания)

        Raises:
            RuntimeError: Если пул не инициализирован
        """
        self._check_pool()

        length = len(content)

        query = """
            INSERT INTO messages (role, content, length, user_id)
            VALUES ($1, $2, $3, $4)
            RETURNING id, created_at
        """

        assert self._pool is not None  # for type checker
        record = await self._pool.fetchrow(query, role, content, length, user_id)

        assert record is not None
        message_id: int = record["id"]
        created_at: datetime = record["created_at"]

        self.logger.debug(
            "Сообщение добавлено в БД",
            message_id=message_id,
            role=role,
            length=length,
            user_id=user_id,
        )

        return message_id, created_at

    async def get_messages(self) -> list[MessageDBDict]:
        """
        Получить все активные (не удаленные) сообщения.

        Returns:
            Список сообщений с метаданными

        Raises:
            RuntimeError: Если пул не инициализирован
        """
        self._check_pool()

        query = """
            SELECT id, role, content, created_at, length, deleted_at
            FROM messages
            WHERE deleted_at IS NULL
            ORDER BY created_at ASC
        """

        assert self._pool is not None  # for type checker
        records = await self._pool.fetch(query)

        messages: list[MessageDBDict] = []
        for record in records:
            messages.append(
                {
                    "id": record["id"],
                    "role": record["role"],
                    "content": record["content"],
                    "created_at": record["created_at"].isoformat(),
                    "length": record["length"],
                    "deleted_at": record["deleted_at"].isoformat()
                    if record["deleted_at"]
                    else None,
                }
            )

        self.logger.debug("Получены сообщения из БД", count=len(messages))

        return messages

    async def soft_delete_message(self, message_id: int) -> None:
        """
        Мягкое удаление сообщения (установка deleted_at).

        Args:
            message_id: ID сообщения для удаления

        Raises:
            RuntimeError: Если пул не инициализирован
        """
        self._check_pool()

        query = """
            UPDATE messages
            SET deleted_at = NOW()
            WHERE id = $1
        """

        assert self._pool is not None  # for type checker
        await self._pool.execute(query, message_id)

        self.logger.debug("Сообщение помечено как удаленное", message_id=message_id)

    async def clear_all_messages(self) -> int:
        """
        Мягкое удаление всех активных сообщений.

        Returns:
            Количество удаленных сообщений

        Raises:
            RuntimeError: Если пул не инициализирован
        """
        self._check_pool()

        query = """
            UPDATE messages
            SET deleted_at = NOW()
            WHERE deleted_at IS NULL
        """

        assert self._pool is not None  # for type checker
        result = await self._pool.execute(query)

        # Результат в формате "UPDATE N", извлекаем число
        deleted_count = int(result.split()[-1]) if result else 0

        self.logger.info("Все сообщения помечены как удаленные", count=deleted_count)

        return deleted_count

    async def get_or_create_user(self, username: str) -> tuple[int, datetime]:
        """
        Получить или создать пользователя по username.

        Если пользователь с таким username существует (и не удален),
        обновляет updated_at и возвращает его id.
        Иначе создает нового пользователя.

        Args:
            username: Имя пользователя

        Returns:
            Tuple с (id пользователя, timestamp создания/обновления)

        Raises:
            RuntimeError: Если пул не инициализирован
        """
        self._check_pool()

        # Ищем активного пользователя с таким username
        query_select = """
            SELECT id, created_at, updated_at
            FROM users
            WHERE username = $1 AND deleted_at IS NULL
        """

        assert self._pool is not None  # for type checker
        record = await self._pool.fetchrow(query_select, username)

        if record:
            # Пользователь найден - обновляем updated_at
            user_id: int = record["id"]
            query_update = """
                UPDATE users
                SET updated_at = NOW()
                WHERE id = $1
                RETURNING updated_at
            """
            update_record = await self._pool.fetchrow(query_update, user_id)
            assert update_record is not None
            updated_at: datetime = update_record["updated_at"]

            self.logger.debug(
                "Пользователь найден и обновлен",
                user_id=user_id,
                username=username,
            )

            return user_id, updated_at
        else:
            # Пользователь не найден - создаем нового
            query_insert = """
                INSERT INTO users (username)
                VALUES ($1)
                RETURNING id, created_at
            """
            insert_record = await self._pool.fetchrow(query_insert, username)
            assert insert_record is not None
            user_id = insert_record["id"]
            created_at: datetime = insert_record["created_at"]

            self.logger.debug(
                "Создан новый пользователь",
                user_id=user_id,
                username=username,
            )

            return user_id, created_at

    async def soft_delete_user(self, user_id: int) -> None:
        """
        Мягкое удаление пользователя (установка deleted_at).

        Args:
            user_id: ID пользователя для удаления

        Raises:
            RuntimeError: Если пул не инициализирован
        """
        self._check_pool()

        query = """
            UPDATE users
            SET deleted_at = NOW()
            WHERE id = $1
        """

        assert self._pool is not None  # for type checker
        await self._pool.execute(query, user_id)

        self.logger.debug("Пользователь помечен как удаленный", user_id=user_id)

    def __repr__(self) -> str:
        """Строковое представление клиента БД."""
        pool_status = "connected" if self._pool else "disconnected"
        return (
            f"DatabaseClient("
            f"status={pool_status}, "
            f"pool_size={self.pool_min_size}-{self.pool_max_size}"
            f")"
        )
