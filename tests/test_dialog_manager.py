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
        manager.add_user_message(f"Вопрос {i+1}")
        manager.add_assistant_message(f"Ответ {i+1}")
    
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

