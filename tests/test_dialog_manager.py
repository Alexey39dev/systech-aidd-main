"""Тесты для DialogManager."""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from src.database import DatabaseClient
from src.dialog_manager import DialogManager


@pytest.fixture
def mock_db():
    """Фикстура для мока DatabaseClient."""
    db = AsyncMock(spec=DatabaseClient)

    # Мокируем add_message - возвращает id и timestamp
    db.add_message = AsyncMock(return_value=(1, datetime(2025, 10, 16, 10, 0, 0)))

    # Мокируем get_messages - возвращает пустой список по умолчанию
    db.get_messages = AsyncMock(return_value=[])

    # Мокируем clear_all_messages
    db.clear_all_messages = AsyncMock(return_value=0)

    # Мокируем soft_delete_message
    db.soft_delete_message = AsyncMock()

    return db


def test_dialog_manager_initialization(mock_db):
    """Тест инициализации DialogManager."""
    manager = DialogManager(db_client=mock_db, user_id=1, max_history=10)

    assert manager.user_id == 1
    assert manager.max_history == 10
    assert manager.db_client is mock_db


@pytest.mark.asyncio
async def test_add_message(mock_db):
    """Тест добавления сообщения в историю."""
    mock_db.get_messages = AsyncMock(
        return_value=[
            {
                "id": 1,
                "role": "user",
                "content": "Привет!",
                "created_at": "2025-10-16T10:00:00",
                "length": 7,
                "deleted_at": None,
            }
        ]
    )

    manager = DialogManager(db_client=mock_db, user_id=1, max_history=5)

    await manager.add_message("user", "Привет!")

    # Проверяем что вызвался add_message на БД
    mock_db.add_message.assert_called_once_with("user", "Привет!", 1)

    # Проверяем что get_history возвращает из БД
    history = await manager.get_history()
    assert len(history) == 1
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Привет!"


@pytest.mark.asyncio
async def test_add_user_and_assistant_messages(mock_db):
    """Тест добавления сообщений пользователя и ассистента."""
    mock_db.get_messages = AsyncMock(
        return_value=[
            {
                "id": 1,
                "role": "user",
                "content": "Как дела?",
                "created_at": "2025-10-16T10:00:00",
                "length": 9,
                "deleted_at": None,
            },
            {
                "id": 2,
                "role": "assistant",
                "content": "Отлично, спасибо!",
                "created_at": "2025-10-16T10:01:00",
                "length": 17,
                "deleted_at": None,
            },
        ]
    )

    manager = DialogManager(db_client=mock_db, user_id=1, max_history=5)

    await manager.add_user_message("Как дела?")
    await manager.add_assistant_message("Отлично, спасибо!")

    history = await manager.get_history()
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Как дела?"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "Отлично, спасибо!"


@pytest.mark.asyncio
async def test_clear_history(mock_db):
    """Тест очистки истории."""
    mock_db.clear_all_messages = AsyncMock(return_value=2)
    mock_db.get_messages = AsyncMock(return_value=[])

    manager = DialogManager(db_client=mock_db, user_id=1, max_history=5)

    await manager.clear_history()

    mock_db.clear_all_messages.assert_called_once()

    history = await manager.get_history()
    assert len(history) == 0


@pytest.mark.asyncio
async def test_history_trimming(mock_db):
    """Тест обрезки истории при превышении лимита."""
    # Мокируем поведение БД для обрезки истории
    messages = []

    async def mock_add(role, content, user_id):
        msg_id = len(messages) + 1
        messages.append(
            {
                "id": msg_id,
                "role": role,
                "content": content,
                "created_at": "2025-10-16T10:00:00",
                "length": len(content),
                "deleted_at": None,
            }
        )
        return (msg_id, datetime(2025, 10, 16, 10, 0, 0))

    async def mock_get():
        return [m for m in messages if m["deleted_at"] is None]

    mock_db.add_message = AsyncMock(side_effect=mock_add)
    mock_db.get_messages = AsyncMock(side_effect=mock_get)
    mock_db.soft_delete_message = AsyncMock()

    manager = DialogManager(db_client=mock_db, user_id=1, max_history=2)

    # Добавляем 3 пары сообщений (6 сообщений)
    for i in range(3):
        await manager.add_user_message(f"Вопрос {i + 1}")
        await manager.add_assistant_message(f"Ответ {i + 1}")

    # Проверяем что вызвался soft_delete для старых сообщений
    assert mock_db.soft_delete_message.called


@pytest.mark.asyncio
async def test_get_conversation_summary(mock_db):
    """Тест получения статистики диалога."""
    mock_db.get_messages = AsyncMock(
        return_value=[
            {
                "id": 1,
                "role": "user",
                "content": "Вопрос 1",
                "created_at": "2025-10-16T10:00:00",
                "length": 8,
                "deleted_at": None,
            },
            {
                "id": 2,
                "role": "assistant",
                "content": "Ответ 1",
                "created_at": "2025-10-16T10:01:00",
                "length": 7,
                "deleted_at": None,
            },
            {
                "id": 3,
                "role": "user",
                "content": "Вопрос 2",
                "created_at": "2025-10-16T10:02:00",
                "length": 8,
                "deleted_at": None,
            },
            {
                "id": 4,
                "role": "assistant",
                "content": "Ответ 2",
                "created_at": "2025-10-16T10:03:00",
                "length": 7,
                "deleted_at": None,
            },
        ]
    )

    manager = DialogManager(db_client=mock_db, user_id=1, max_history=5)

    summary = await manager.get_conversation_summary()

    assert summary["total_messages"] == 4
    assert summary["user_messages"] == 2
    assert summary["assistant_messages"] == 2
    assert summary["max_history"] == 5


@pytest.mark.asyncio
async def test_empty_message_handling(mock_db):
    """Тест обработки пустых сообщений."""
    mock_db.get_messages = AsyncMock(return_value=[])
    manager = DialogManager(db_client=mock_db, user_id=1, max_history=5)

    # Пустые сообщения не должны добавляться
    await manager.add_message("user", "")
    await manager.add_message("user", "   ")

    # add_message не должен вызываться для пустых сообщений
    mock_db.add_message.assert_not_called()


@pytest.mark.asyncio
async def test_get_history_returns_copy(mock_db):
    """Тест что get_history возвращает копию, а не оригинал."""
    mock_db.get_messages = AsyncMock(
        return_value=[
            {
                "id": 1,
                "role": "user",
                "content": "Тест",
                "created_at": "2025-10-16T10:00:00",
                "length": 4,
                "deleted_at": None,
            }
        ]
    )

    manager = DialogManager(db_client=mock_db, user_id=1, max_history=5)

    history1 = await manager.get_history()
    history2 = await manager.get_history()

    # Изменение одной копии не должно влиять на другую
    history1.append({"role": "user", "content": "Новое"})

    assert len(history1) == 2
    assert len(history2) == 1


def test_repr(mock_db):
    """Тест строкового представления."""
    manager = DialogManager(db_client=mock_db, user_id=1, max_history=10)

    repr_str = repr(manager)
    assert "DialogManager" in repr_str
    assert "max_history=10" in repr_str


@pytest.mark.asyncio
async def test_len(mock_db):
    """Тест использования len()."""
    mock_db.get_messages = AsyncMock(return_value=[])
    manager = DialogManager(db_client=mock_db, user_id=1, max_history=5)

    # __len__ теперь async, нельзя использовать напрямую len()
    # Используем get_history_length()
    length = await manager.get_history_length()
    assert length == 0


# === Параметризованные тесты ===


@pytest.mark.parametrize("max_history", [1, 5, 10, 50])
@pytest.mark.asyncio
async def test_history_trimming_parametrized(max_history, mock_db):
    """Тест обрезки истории при разных значениях max_history."""
    messages = []

    async def mock_add(role, content, user_id):
        msg_id = len(messages) + 1
        messages.append(
            {
                "id": msg_id,
                "role": role,
                "content": content,
                "created_at": "2025-10-16T10:00:00",
                "length": len(content),
                "deleted_at": None,
            }
        )
        return (msg_id, datetime(2025, 10, 16, 10, 0, 0))

    mock_db.add_message = AsyncMock(side_effect=mock_add)
    mock_db.get_messages = AsyncMock(
        side_effect=lambda: [m for m in messages if m["deleted_at"] is None]
    )
    mock_db.soft_delete_message = AsyncMock()

    manager = DialogManager(db_client=mock_db, user_id=1, max_history=max_history)

    # Добавляем в 3 раза больше сообщений чем лимит
    for i in range(max_history * 3):
        await manager.add_user_message(f"msg {i}")
        await manager.add_assistant_message(f"response {i}")

    # Проверяем что вызвался soft_delete
    assert mock_db.soft_delete_message.called


@pytest.mark.parametrize("role", ["user", "assistant", "system"])
@pytest.mark.asyncio
async def test_add_message_with_different_roles(role, mock_db):
    """Тест добавления сообщений с разными ролями."""
    mock_db.get_messages = AsyncMock(
        return_value=[
            {
                "id": 1,
                "role": role,
                "content": "Test message",
                "created_at": "2025-10-16T10:00:00",
                "length": 12,
                "deleted_at": None,
            }
        ]
    )

    manager = DialogManager(db_client=mock_db, user_id=1, max_history=5)

    await manager.add_message(role, "Test message")

    history = await manager.get_history()
    assert len(history) == 1
    assert history[0]["role"] == role
    assert history[0]["content"] == "Test message"


# === Тесты с system role ===


@pytest.mark.asyncio
async def test_add_system_message(mock_db):
    """Тест добавления системного сообщения."""
    mock_db.get_messages = AsyncMock(
        return_value=[
            {
                "id": 1,
                "role": "system",
                "content": "You are a helpful assistant",
                "created_at": "2025-10-16T10:00:00",
                "length": 28,
                "deleted_at": None,
            },
            {
                "id": 2,
                "role": "user",
                "content": "Hello",
                "created_at": "2025-10-16T10:01:00",
                "length": 5,
                "deleted_at": None,
            },
            {
                "id": 3,
                "role": "assistant",
                "content": "Hi there!",
                "created_at": "2025-10-16T10:02:00",
                "length": 9,
                "deleted_at": None,
            },
        ]
    )

    manager = DialogManager(db_client=mock_db, user_id=1, max_history=5)

    await manager.add_message("system", "You are a helpful assistant")
    await manager.add_user_message("Hello")
    await manager.add_assistant_message("Hi there!")

    history = await manager.get_history()
    assert len(history) == 3
    assert history[0]["role"] == "system"
    assert history[1]["role"] == "user"
    assert history[2]["role"] == "assistant"


@pytest.mark.asyncio
async def test_conversation_summary_with_system(mock_db):
    """Тест статистики с системными сообщениями."""
    mock_db.get_messages = AsyncMock(
        return_value=[
            {
                "id": 1,
                "role": "system",
                "content": "System prompt",
                "created_at": "2025-10-16T10:00:00",
                "length": 13,
                "deleted_at": None,
            },
            {
                "id": 2,
                "role": "user",
                "content": "Hello",
                "created_at": "2025-10-16T10:01:00",
                "length": 5,
                "deleted_at": None,
            },
            {
                "id": 3,
                "role": "assistant",
                "content": "Hi",
                "created_at": "2025-10-16T10:02:00",
                "length": 2,
                "deleted_at": None,
            },
        ]
    )

    manager = DialogManager(db_client=mock_db, user_id=1, max_history=5)

    stats = await manager.get_conversation_summary()
    # System не считается в user/assistant
    assert stats["user_messages"] == 1
    assert stats["assistant_messages"] == 1
    assert stats["total_messages"] == 3


# === Edge cases: граничные значения ===


@pytest.mark.parametrize("max_history", [1, 100])
def test_edge_case_max_history(max_history, mock_db):
    """Тест граничных значений max_history."""
    manager = DialogManager(db_client=mock_db, user_id=1, max_history=max_history)
    assert manager.max_history == max_history


def test_zero_max_history(mock_db):
    """Тест max_history=0 (граничный случай)."""
    manager = DialogManager(db_client=mock_db, user_id=1, max_history=0)
    assert manager.max_history == 0


def test_default_max_history(mock_db):
    """Тест значения max_history по умолчанию."""
    manager = DialogManager(db_client=mock_db, user_id=1, max_history=10)
    assert manager.max_history == 10  # Дефолтное значение


# === Тесты с unicode и emoji ===


@pytest.mark.asyncio
async def test_unicode_and_emoji_messages(mock_db):
    """Тест сообщений с unicode и emoji."""
    mock_db.get_messages = AsyncMock(
        return_value=[
            {
                "id": 1,
                "role": "user",
                "content": "Привет! 👋 How are you? 你好",
                "created_at": "2025-10-16T10:00:00",
                "length": 30,
                "deleted_at": None,
            },
            {
                "id": 2,
                "role": "assistant",
                "content": "I'm fine! ✨ Спасибо 谢谢",
                "created_at": "2025-10-16T10:01:00",
                "length": 26,
                "deleted_at": None,
            },
        ]
    )

    manager = DialogManager(db_client=mock_db, user_id=1, max_history=5)

    history = await manager.get_history()
    assert "👋" in history[0]["content"]
    assert "✨" in history[1]["content"]
    assert "Привет" in history[0]["content"]
    assert "你好" in history[0]["content"]


@pytest.mark.asyncio
async def test_special_characters(mock_db):
    """Тест специальных символов в сообщениях."""
    special_msg = "Test with special chars: \n\t@#$%^&*()_+{}[]|\\:;<>?,./~`"
    mock_db.get_messages = AsyncMock(
        return_value=[
            {
                "id": 1,
                "role": "user",
                "content": special_msg,
                "created_at": "2025-10-16T10:00:00",
                "length": len(special_msg),
                "deleted_at": None,
            }
        ]
    )

    manager = DialogManager(db_client=mock_db, user_id=1, max_history=5)

    history = await manager.get_history()
    assert history[0]["content"] == special_msg


# === Тесты со смешанными ролями ===


@pytest.mark.asyncio
async def test_mixed_message_roles(mock_db):
    """Тест смешанных ролей сообщений (не обязательно пары)."""
    mock_db.get_messages = AsyncMock(
        return_value=[
            {
                "id": 1,
                "role": "system",
                "content": "System prompt",
                "created_at": "2025-10-16T10:00:00",
                "length": 13,
                "deleted_at": None,
            },
            {
                "id": 2,
                "role": "user",
                "content": "User 1",
                "created_at": "2025-10-16T10:01:00",
                "length": 6,
                "deleted_at": None,
            },
            {
                "id": 3,
                "role": "user",
                "content": "User 2",
                "created_at": "2025-10-16T10:02:00",
                "length": 6,
                "deleted_at": None,
            },
            {
                "id": 4,
                "role": "assistant",
                "content": "Assistant 1",
                "created_at": "2025-10-16T10:03:00",
                "length": 11,
                "deleted_at": None,
            },
        ]
    )

    manager = DialogManager(db_client=mock_db, user_id=1, max_history=5)

    stats = await manager.get_conversation_summary()
    assert stats["total_messages"] == 4
    assert stats["user_messages"] == 2
    assert stats["assistant_messages"] == 1


@pytest.mark.asyncio
async def test_multiple_consecutive_same_role(mock_db):
    """Тест нескольких последовательных сообщений одной роли."""
    mock_db.get_messages = AsyncMock(
        return_value=[
            {
                "id": 1,
                "role": "user",
                "content": "Question 1",
                "created_at": "2025-10-16T10:00:00",
                "length": 10,
                "deleted_at": None,
            },
            {
                "id": 2,
                "role": "user",
                "content": "Question 2",
                "created_at": "2025-10-16T10:01:00",
                "length": 10,
                "deleted_at": None,
            },
            {
                "id": 3,
                "role": "user",
                "content": "Question 3",
                "created_at": "2025-10-16T10:02:00",
                "length": 10,
                "deleted_at": None,
            },
            {
                "id": 4,
                "role": "assistant",
                "content": "Answer to all",
                "created_at": "2025-10-16T10:03:00",
                "length": 13,
                "deleted_at": None,
            },
        ]
    )

    manager = DialogManager(db_client=mock_db, user_id=1, max_history=10)

    history = await manager.get_history()
    assert len(history) == 4
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "user"
    assert history[2]["role"] == "user"
    assert history[3]["role"] == "assistant"


# === Тесты с очень длинными сообщениями ===


@pytest.mark.asyncio
async def test_very_long_messages(mock_db):
    """Тест очень длинных сообщений."""
    long_message = "A" * 10000  # 10К символов
    mock_db.get_messages = AsyncMock(
        return_value=[
            {
                "id": 1,
                "role": "user",
                "content": long_message,
                "created_at": "2025-10-16T10:00:00",
                "length": 10000,
                "deleted_at": None,
            }
        ]
    )

    manager = DialogManager(db_client=mock_db, user_id=1, max_history=5)

    history = await manager.get_history()
    assert len(history[0]["content"]) == 10000
    assert history[0]["content"] == long_message


@pytest.mark.asyncio
async def test_extremely_long_message(mock_db):
    """Тест экстремально длинного сообщения."""
    very_long_message = "B" * 100000
    mock_db.get_messages = AsyncMock(
        return_value=[
            {
                "id": 1,
                "role": "assistant",
                "content": very_long_message,
                "created_at": "2025-10-16T10:00:00",
                "length": 100000,
                "deleted_at": None,
            }
        ]
    )

    manager = DialogManager(db_client=mock_db, user_id=1, max_history=5)

    history = await manager.get_history()
    assert len(history[0]["content"]) == 100000


# === Дополнительные edge cases ===


@pytest.mark.asyncio
async def test_clear_empty_history(mock_db):
    """Тест очистки уже пустой истории."""
    mock_db.get_messages = AsyncMock(return_value=[])
    mock_db.clear_all_messages = AsyncMock(return_value=0)

    manager = DialogManager(db_client=mock_db, user_id=1, max_history=5)

    # История уже пуста
    await manager.clear_history()
    mock_db.clear_all_messages.assert_called_once()


@pytest.mark.asyncio
async def test_get_summary_empty_history(mock_db):
    """Тест получения статистики из пустой истории."""
    mock_db.get_messages = AsyncMock(return_value=[])

    manager = DialogManager(db_client=mock_db, user_id=1, max_history=5)

    stats = await manager.get_conversation_summary()
    assert stats["total_messages"] == 0
    assert stats["user_messages"] == 0
    assert stats["assistant_messages"] == 0
    assert stats["max_history"] == 5


def test_repr_empty_manager(mock_db):
    """Тест repr для пустого менеджера."""
    manager = DialogManager(db_client=mock_db, user_id=1, max_history=15)

    repr_str = repr(manager)
    assert "DialogManager" in repr_str
    assert "max_history=15" in repr_str
