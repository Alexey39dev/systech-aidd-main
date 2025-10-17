"""Тесты для DatabaseClient."""

from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from src.database import DatabaseClient


@pytest.fixture
def mock_pool():
    """Фикстура для мока asyncpg pool."""
    pool = AsyncMock()
    pool.close = AsyncMock()
    return pool


@pytest.fixture
def db_client():
    """Фикстура для DatabaseClient."""
    return DatabaseClient(
        database_url="postgresql://user:pass@localhost:5432/test_db",
        pool_min_size=2,
        pool_max_size=5,
    )


class TestDatabaseClientInitialization:
    """Тесты инициализации DatabaseClient."""

    def test_initialization(self):
        """Тест создания экземпляра DatabaseClient."""
        client = DatabaseClient(
            database_url="postgresql://user:pass@localhost/db", pool_min_size=5, pool_max_size=20
        )

        assert client.database_url == "postgresql://user:pass@localhost/db"
        assert client.pool_min_size == 5
        assert client.pool_max_size == 20
        assert client._pool is None

    def test_initialization_with_defaults(self):
        """Тест создания с минимальными параметрами."""
        client = DatabaseClient(database_url="postgresql://localhost/db")

        assert client.database_url == "postgresql://localhost/db"
        assert client.pool_min_size == 5  # default
        assert client.pool_max_size == 20  # default


class TestDatabaseClientConnection:
    """Тесты подключения к БД."""

    @pytest.mark.asyncio
    async def test_connect_creates_pool(self, db_client, mock_pool):
        """Тест создания пула соединений."""
        with patch(
            "src.database.asyncpg.create_pool", new=AsyncMock(return_value=mock_pool)
        ) as mock_create:
            await db_client.connect()

            mock_create.assert_called_once_with(
                db_client.database_url,
                min_size=db_client.pool_min_size,
                max_size=db_client.pool_max_size,
            )
            assert db_client._pool is mock_pool

    @pytest.mark.asyncio
    async def test_close_closes_pool(self, db_client, mock_pool):
        """Тест закрытия пула соединений."""
        db_client._pool = mock_pool

        await db_client.close()

        mock_pool.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_without_pool(self, db_client):
        """Тест закрытия когда пула нет."""
        # Не должно падать
        await db_client.close()
        assert db_client._pool is None


class TestDatabaseClientAddMessage:
    """Тесты добавления сообщений."""

    @pytest.mark.asyncio
    async def test_add_message_inserts_with_metadata(self, db_client, mock_pool):
        """Тест добавления сообщения с метаданными."""
        # Мокируем результат из БД
        mock_record = {"id": 1, "created_at": datetime(2025, 10, 16, 10, 0, 0)}
        mock_pool.fetchrow = AsyncMock(return_value=mock_record)
        db_client._pool = mock_pool

        message_id, created_at = await db_client.add_message("user", "Test message", user_id=42)

        # Проверяем вызов с правильными параметрами
        mock_pool.fetchrow.assert_called_once()
        call_args = mock_pool.fetchrow.call_args[0]
        assert "INSERT INTO messages" in call_args[0]
        assert "role" in call_args[0]
        assert "content" in call_args[0]
        assert "length" in call_args[0]
        assert call_args[1] == "user"
        assert call_args[2] == "Test message"
        assert call_args[3] == 12  # len("Test message")
        assert call_args[4] == 42  # user_id

        assert message_id == 1
        assert created_at == datetime(2025, 10, 16, 10, 0, 0)

    @pytest.mark.asyncio
    async def test_add_message_calculates_length(self, db_client, mock_pool):
        """Тест автоматического подсчета длины сообщения."""
        mock_record = {"id": 1, "created_at": datetime.now()}
        mock_pool.fetchrow = AsyncMock(return_value=mock_record)
        db_client._pool = mock_pool

        await db_client.add_message("assistant", "Привет! 👋", user_id=1)

        call_args = mock_pool.fetchrow.call_args[0]
        assert call_args[3] == len("Привет! 👋")  # Должно правильно считать unicode
        assert call_args[4] == 1  # user_id


class TestDatabaseClientGetMessages:
    """Тесты получения сообщений."""

    @pytest.mark.asyncio
    async def test_get_messages_returns_only_active(self, db_client, mock_pool):
        """Тест получения только активных (не удаленных) сообщений."""
        mock_records = [
            {
                "id": 1,
                "role": "user",
                "content": "Hello",
                "created_at": datetime(2025, 10, 16, 10, 0, 0),
                "length": 5,
                "deleted_at": None,
            },
            {
                "id": 2,
                "role": "assistant",
                "content": "Hi there!",
                "created_at": datetime(2025, 10, 16, 10, 1, 0),
                "length": 9,
                "deleted_at": None,
            },
        ]
        mock_pool.fetch = AsyncMock(return_value=mock_records)
        db_client._pool = mock_pool

        messages = await db_client.get_messages()

        # Проверяем SQL запрос
        mock_pool.fetch.assert_called_once()
        call_args = mock_pool.fetch.call_args[0]
        assert "SELECT" in call_args[0]
        assert "WHERE deleted_at IS NULL" in call_args[0]
        assert "ORDER BY created_at ASC" in call_args[0]

        # Проверяем результат
        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Hello"
        assert messages[1]["role"] == "assistant"

    @pytest.mark.asyncio
    async def test_get_messages_empty_result(self, db_client, mock_pool):
        """Тест получения пустого списка."""
        mock_pool.fetch = AsyncMock(return_value=[])
        db_client._pool = mock_pool

        messages = await db_client.get_messages()

        assert messages == []


class TestDatabaseClientSoftDelete:
    """Тесты мягкого удаления."""

    @pytest.mark.asyncio
    async def test_soft_delete_message(self, db_client, mock_pool):
        """Тест мягкого удаления одного сообщения."""
        mock_pool.execute = AsyncMock()
        db_client._pool = mock_pool

        await db_client.soft_delete_message(1)

        mock_pool.execute.assert_called_once()
        call_args = mock_pool.execute.call_args[0]
        assert "UPDATE messages" in call_args[0]
        assert "SET deleted_at = NOW()" in call_args[0]
        assert "WHERE id = $1" in call_args[0]
        assert call_args[1] == 1

    @pytest.mark.asyncio
    async def test_clear_all_messages(self, db_client, mock_pool):
        """Тест мягкого удаления всех активных сообщений."""
        mock_pool.execute = AsyncMock(return_value="UPDATE 5")
        db_client._pool = mock_pool

        deleted_count = await db_client.clear_all_messages()

        mock_pool.execute.assert_called_once()
        call_args = mock_pool.execute.call_args[0]
        assert "UPDATE messages" in call_args[0]
        assert "SET deleted_at = NOW()" in call_args[0]
        assert "WHERE deleted_at IS NULL" in call_args[0]

        assert deleted_count == 5


class TestDatabaseClientEdgeCases:
    """Тесты граничных случаев и ошибок."""

    @pytest.mark.asyncio
    async def test_add_message_raises_without_connection(self, db_client):
        """Тест что add_message падает без подключения."""
        with pytest.raises(RuntimeError, match="Database pool not initialized"):
            await db_client.add_message("user", "test", user_id=1)

    @pytest.mark.asyncio
    async def test_get_messages_raises_without_connection(self, db_client):
        """Тест что get_messages падает без подключения."""
        with pytest.raises(RuntimeError, match="Database pool not initialized"):
            await db_client.get_messages()


class TestDatabaseClientUserMethods:
    """Тесты для методов работы с пользователями."""

    @pytest.mark.asyncio
    async def test_get_or_create_user_creates_new_user(self, db_client, mock_pool):
        """Тест создания нового пользователя."""
        # Мокируем что пользователь не найден
        mock_pool.fetchrow = AsyncMock(
            side_effect=[
                None,  # SELECT - пользователь не найден
                {"id": 1, "created_at": datetime(2025, 10, 16, 10, 0, 0)},  # INSERT
            ]
        )
        db_client._pool = mock_pool

        user_id, created_at = await db_client.get_or_create_user("testuser")

        assert user_id == 1
        assert isinstance(created_at, datetime)
        assert mock_pool.fetchrow.call_count == 2

        # Проверяем первый вызов (SELECT)
        first_call = mock_pool.fetchrow.call_args_list[0]
        assert "SELECT id" in first_call[0][0]
        assert "FROM users" in first_call[0][0]
        assert first_call[0][1] == "testuser"

        # Проверяем второй вызов (INSERT)
        second_call = mock_pool.fetchrow.call_args_list[1]
        assert "INSERT INTO users" in second_call[0][0]
        assert second_call[0][1] == "testuser"

    @pytest.mark.asyncio
    async def test_get_or_create_user_updates_existing_user(self, db_client, mock_pool):
        """Тест обновления существующего пользователя."""
        # Мокируем что пользователь найден
        mock_pool.fetchrow = AsyncMock(
            side_effect=[
                {
                    "id": 5,
                    "created_at": datetime(2025, 10, 15, 10, 0, 0),
                    "updated_at": datetime(2025, 10, 15, 10, 0, 0),
                },  # SELECT
                {"updated_at": datetime(2025, 10, 16, 12, 0, 0)},  # UPDATE
            ]
        )
        db_client._pool = mock_pool

        user_id, updated_at = await db_client.get_or_create_user("existinguser")

        assert user_id == 5
        assert isinstance(updated_at, datetime)
        assert mock_pool.fetchrow.call_count == 2

        # Проверяем первый вызов (SELECT)
        first_call = mock_pool.fetchrow.call_args_list[0]
        assert "SELECT id" in first_call[0][0]
        assert first_call[0][1] == "existinguser"

        # Проверяем второй вызов (UPDATE)
        second_call = mock_pool.fetchrow.call_args_list[1]
        assert "UPDATE users" in second_call[0][0]
        assert "SET updated_at = NOW()" in second_call[0][0]
        assert second_call[0][1] == 5

    @pytest.mark.asyncio
    async def test_soft_delete_user(self, db_client, mock_pool):
        """Тест мягкого удаления пользователя."""
        mock_pool.execute = AsyncMock(return_value="UPDATE 1")
        db_client._pool = mock_pool

        await db_client.soft_delete_user(42)

        mock_pool.execute.assert_called_once()
        call_args = mock_pool.execute.call_args[0]
        assert "UPDATE users" in call_args[0]
        assert "SET deleted_at = NOW()" in call_args[0]
        assert "WHERE id = $1" in call_args[0]
        assert call_args[1] == 42

    @pytest.mark.asyncio
    async def test_get_or_create_user_raises_without_connection(self, db_client):
        """Тест что get_or_create_user падает без подключения."""
        with pytest.raises(RuntimeError, match="Database pool not initialized"):
            await db_client.get_or_create_user("testuser")

    @pytest.mark.asyncio
    async def test_soft_delete_user_raises_without_connection(self, db_client):
        """Тест что soft_delete_user падает без подключения."""
        with pytest.raises(RuntimeError, match="Database pool not initialized"):
            await db_client.soft_delete_user(1)
