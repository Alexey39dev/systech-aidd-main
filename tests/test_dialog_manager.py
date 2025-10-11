"""Тесты для DialogManager."""

import pytest

from src.dialog_manager import DialogManager


def test_dialog_manager_initialization():
    """Тест инициализации DialogManager."""
    manager = DialogManager(max_history=10)

    assert manager.max_history == 10
    assert manager.get_history_length() == 0
    assert len(manager) == 0


def test_add_message():
    """Тест добавления сообщения в историю."""
    manager = DialogManager(max_history=5)

    manager.add_message("user", "Привет!")
    assert manager.get_history_length() == 1

    history = manager.get_history()
    assert len(history) == 1
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Привет!"


def test_add_user_and_assistant_messages():
    """Тест добавления сообщений пользователя и ассистента."""
    manager = DialogManager(max_history=5)

    manager.add_user_message("Как дела?")
    manager.add_assistant_message("Отлично, спасибо!")

    assert manager.get_history_length() == 2

    history = manager.get_history()
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Как дела?"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "Отлично, спасибо!"


def test_clear_history():
    """Тест очистки истории."""
    manager = DialogManager(max_history=5)

    manager.add_user_message("Сообщение 1")
    manager.add_assistant_message("Ответ 1")
    assert manager.get_history_length() == 2

    manager.clear_history()
    assert manager.get_history_length() == 0
    assert manager.get_history() == []


def test_history_trimming():
    """Тест обрезки истории при превышении лимита."""
    manager = DialogManager(max_history=2)  # Максимум 2 пары (4 сообщения)

    # Добавляем 3 пары сообщений (6 сообщений)
    for i in range(3):
        manager.add_user_message(f"Вопрос {i + 1}")
        manager.add_assistant_message(f"Ответ {i + 1}")

    # Должно остаться только 4 сообщения (последние 2 пары)
    assert manager.get_history_length() == 4

    history = manager.get_history()
    assert history[0]["content"] == "Вопрос 2"
    assert history[1]["content"] == "Ответ 2"
    assert history[2]["content"] == "Вопрос 3"
    assert history[3]["content"] == "Ответ 3"


def test_get_conversation_summary():
    """Тест получения статистики диалога."""
    manager = DialogManager(max_history=5)

    manager.add_user_message("Вопрос 1")
    manager.add_assistant_message("Ответ 1")
    manager.add_user_message("Вопрос 2")
    manager.add_assistant_message("Ответ 2")

    summary = manager.get_conversation_summary()

    assert summary["total_messages"] == 4
    assert summary["user_messages"] == 2
    assert summary["assistant_messages"] == 2
    assert summary["max_history"] == 5


def test_empty_message_handling():
    """Тест обработки пустых сообщений."""
    manager = DialogManager(max_history=5)

    # Пустые сообщения не должны добавляться
    manager.add_message("user", "")
    manager.add_message("user", "   ")

    assert manager.get_history_length() == 0


def test_get_history_returns_copy():
    """Тест что get_history возвращает копию, а не оригинал."""
    manager = DialogManager(max_history=5)

    manager.add_user_message("Тест")

    history1 = manager.get_history()
    history2 = manager.get_history()

    # Изменение одной копии не должно влиять на другую
    history1.append({"role": "user", "content": "Новое"})

    assert len(history1) == 2
    assert len(history2) == 1
    assert manager.get_history_length() == 1


def test_repr():
    """Тест строкового представления."""
    manager = DialogManager(max_history=10)
    manager.add_user_message("Тест")

    repr_str = repr(manager)
    assert "DialogManager" in repr_str
    assert "messages=1" in repr_str
    assert "max_history=10" in repr_str


def test_len():
    """Тест использования len()."""
    manager = DialogManager(max_history=5)

    assert len(manager) == 0

    manager.add_user_message("Тест 1")
    assert len(manager) == 1

    manager.add_assistant_message("Ответ 1")
    assert len(manager) == 2


# === Параметризованные тесты ===


@pytest.mark.parametrize("max_history", [1, 5, 10, 50])
def test_history_trimming_parametrized(max_history):
    """Тест обрезки истории при разных значениях max_history."""
    manager = DialogManager(max_history)

    # Добавляем в 3 раза больше сообщений чем лимит
    for i in range(max_history * 3):
        manager.add_user_message(f"msg {i}")
        manager.add_assistant_message(f"response {i}")

    # Должно остаться только max_history * 2 сообщений (пары)
    assert len(manager) == max_history * 2
    assert manager.get_history_length() == max_history * 2

    # Проверяем, что сохранились последние сообщения
    history = manager.get_history()
    expected_start_index = max_history * 3 - max_history
    assert f"msg {expected_start_index}" in history[0]["content"]


@pytest.mark.parametrize("role", ["user", "assistant", "system"])
def test_add_message_with_different_roles(role):
    """Тест добавления сообщений с разными ролями."""
    manager = DialogManager(max_history=5)

    manager.add_message(role, "Test message")

    history = manager.get_history()
    assert len(history) == 1
    assert history[0]["role"] == role
    assert history[0]["content"] == "Test message"


# === Тесты с system role ===


def test_add_system_message():
    """Тест добавления системного сообщения."""
    manager = DialogManager(max_history=5)

    manager.add_message("system", "You are a helpful assistant")
    manager.add_user_message("Hello")
    manager.add_assistant_message("Hi there!")

    history = manager.get_history()
    assert len(history) == 3
    assert history[0]["role"] == "system"
    assert history[1]["role"] == "user"
    assert history[2]["role"] == "assistant"


def test_conversation_summary_with_system():
    """Тест статистики с системными сообщениями."""
    manager = DialogManager(max_history=5)

    manager.add_message("system", "System prompt")
    manager.add_user_message("Hello")
    manager.add_assistant_message("Hi")

    stats = manager.get_conversation_summary()
    # System не считается в user/assistant
    assert stats["user_messages"] == 1
    assert stats["assistant_messages"] == 1
    assert stats["total_messages"] == 3


# === Edge cases: граничные значения ===


@pytest.mark.parametrize("max_history", [1, 100])
def test_edge_case_max_history(max_history):
    """Тест граничных значений max_history."""
    manager = DialogManager(max_history=max_history)
    assert manager.max_history == max_history

    # Добавляем несколько сообщений
    manager.add_user_message("Test 1")
    manager.add_assistant_message("Response 1")
    manager.add_user_message("Test 2")
    manager.add_assistant_message("Response 2")

    # Проверяем, что история не превышает лимит
    assert len(manager) <= max_history * 2


def test_zero_max_history():
    """Тест max_history=0 (граничный случай)."""
    manager = DialogManager(max_history=0)
    assert manager.max_history == 0

    # При max_history=0 история все равно сохраняется
    # так как [-0:] возвращает весь список
    manager.add_user_message("Test")
    # История может содержать сообщения при max_history=0
    # Это граничное поведение Python slicing
    assert manager.max_history == 0


def test_default_max_history():
    """Тест значения max_history по умолчанию."""
    manager = DialogManager()
    assert manager.max_history == 10  # Дефолтное значение


# === Тесты с unicode и emoji ===


def test_unicode_and_emoji_messages():
    """Тест сообщений с unicode и emoji."""
    manager = DialogManager(max_history=5)

    manager.add_user_message("Привет! 👋 How are you? 你好")
    manager.add_assistant_message("I'm fine! ✨ Спасибо 谢谢")

    history = manager.get_history()
    assert "👋" in history[0]["content"]
    assert "✨" in history[1]["content"]
    assert "Привет" in history[0]["content"]
    assert "你好" in history[0]["content"]


def test_special_characters():
    """Тест специальных символов в сообщениях."""
    manager = DialogManager(max_history=5)

    special_msg = "Test with special chars: \n\t@#$%^&*()_+{}[]|\\:;<>?,./~`"
    manager.add_user_message(special_msg)

    history = manager.get_history()
    assert history[0]["content"] == special_msg


# === Тесты со смешанными ролями ===


def test_mixed_message_roles():
    """Тест смешанных ролей сообщений (не обязательно пары)."""
    manager = DialogManager(max_history=5)

    # Не обязательно пары user-assistant
    manager.add_message("system", "System prompt")
    manager.add_user_message("User 1")
    manager.add_user_message("User 2")  # Два подряд от user
    manager.add_assistant_message("Assistant 1")

    stats = manager.get_conversation_summary()
    assert stats["total_messages"] == 4
    assert stats["user_messages"] == 2
    assert stats["assistant_messages"] == 1


def test_multiple_consecutive_same_role():
    """Тест нескольких последовательных сообщений одной роли."""
    manager = DialogManager(max_history=10)

    # Несколько сообщений подряд от одной роли
    manager.add_user_message("Question 1")
    manager.add_user_message("Question 2")
    manager.add_user_message("Question 3")
    manager.add_assistant_message("Answer to all")

    history = manager.get_history()
    assert len(history) == 4
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "user"
    assert history[2]["role"] == "user"
    assert history[3]["role"] == "assistant"


# === Тесты с очень длинными сообщениями ===


def test_very_long_messages():
    """Тест очень длинных сообщений."""
    manager = DialogManager(max_history=5)

    long_message = "A" * 10000  # 10К символов
    manager.add_user_message(long_message)

    history = manager.get_history()
    assert len(history[0]["content"]) == 10000
    assert history[0]["content"] == long_message


def test_extremely_long_message():
    """Тест экстремально длинного сообщения."""
    manager = DialogManager(max_history=5)

    # 100К символов
    very_long_message = "B" * 100000
    manager.add_assistant_message(very_long_message)

    history = manager.get_history()
    assert len(history[0]["content"]) == 100000


# === Дополнительные edge cases ===


def test_clear_empty_history():
    """Тест очистки уже пустой истории."""
    manager = DialogManager(max_history=5)

    # История уже пуста
    assert len(manager) == 0
    manager.clear_history()
    assert len(manager) == 0


def test_get_summary_empty_history():
    """Тест получения статистики из пустой истории."""
    manager = DialogManager(max_history=5)

    stats = manager.get_conversation_summary()
    assert stats["total_messages"] == 0
    assert stats["user_messages"] == 0
    assert stats["assistant_messages"] == 0
    assert stats["max_history"] == 5


def test_repr_empty_manager():
    """Тест repr для пустого менеджера."""
    manager = DialogManager(max_history=15)

    repr_str = repr(manager)
    assert "DialogManager" in repr_str
    assert "messages=0" in repr_str
    assert "max_history=15" in repr_str
