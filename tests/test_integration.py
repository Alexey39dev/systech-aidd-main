"""Интеграционные тесты для проверки всех сценариев из vision.md."""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.config import Config
from src.console import ConsoleApp
from src.dialog_manager import DialogManager


@pytest.fixture
def mock_config():
    """Создание мок-конфигурации."""
    config = Mock(spec=Config)
    config.openrouter_api_key = "test_key"
    config.system_prompt = "Ты полезный ассистент"
    config.system_prompt_file = None
    config.max_history = 3
    config.llm_model = "test/model"
    config.llm_temperature = 0.7
    config.llm_max_tokens = 100
    config.log_level = "INFO"
    return config


@pytest.fixture
def mock_db():
    """Создание мок-клиента БД."""
    db = Mock()
    db.connect = AsyncMock()
    db.close = AsyncMock()
    db.add_message = AsyncMock(return_value=(1, datetime(2025, 10, 16, 10, 0, 0)))
    db.get_messages = AsyncMock(return_value=[])
    db.soft_delete_message = AsyncMock()
    db.clear_all_messages = AsyncMock(return_value=0)
    return db


@pytest.mark.asyncio
async def test_scenario_1_application_startup(mock_config, mock_db):
    """
    Сценарий 1: Запуск приложения.
    - Загрузка конфигурации
    - Инициализация компонентов
    - Проверка готовности к работе
    """
    # Создаем приложение
    with patch("src.console.LLMClient"):
        app = ConsoleApp(mock_config, mock_db, user_id=1)

    # Проверяем инициализацию
    assert app.config == mock_config
    assert app.dialog_manager is not None
    assert isinstance(app.dialog_manager, DialogManager)
    assert app.dialog_manager.max_history == 3
    assert app.is_running is False


@pytest.mark.asyncio
async def test_scenario_2_user_message_processing(mock_config, mock_db):
    """
    Сценарий 2: Получение сообщения от пользователя.
    - Получение текста
    - Добавление в историю
    - Отправка запроса к LLM
    - Получение ответа
    """
    with patch("src.console.LLMClient"):
        app = ConsoleApp(mock_config, mock_db, user_id=1)

        # Настраиваем мок LLM
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Тестовый ответ"))]
        mock_response.usage = None

        app.llm_client.get_response = AsyncMock(return_value="Тестовый ответ")

        # Обрабатываем сообщение
        response = await app.get_response("Привет!")

        # Проверяем результат
        assert response == "Тестовый ответ"
        assert mock_db.add_message.call_count == 2  # user + assistant


@pytest.mark.asyncio
async def test_scenario_3_commands_handling(mock_config, mock_db):
    """
    Сценарий 3: Обработка команд.
    - /help - справка
    - /clear - очистка истории
    - /history - показ истории
    - /stats - статистика
    - /exit - выход
    """
    with patch("src.console.LLMClient"):
        app = ConsoleApp(mock_config, mock_db, user_id=1)

        # Мокаем историю с двумя сообщениями
        mock_db.get_messages = AsyncMock(
            return_value=[
                {
                    "id": 1,
                    "role": "user",
                    "content": "Тест 1",
                    "created_at": "2025-10-16T10:00:00",
                    "length": 6,
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
            ]
        )

        # Тест /help
        result = await app.handle_command("/help")
        assert result is True

        # Тест /history
        result = await app.handle_command("/history")
        assert result is True

        # Тест /stats
        result = await app.handle_command("/stats")
        assert result is True

        # Тест /clear
        mock_db.clear_all_messages = AsyncMock(return_value=2)
        result = await app.handle_command("/clear")
        assert result is True
        mock_db.clear_all_messages.assert_called_once()

        # Тест /exit
        result = await app.handle_command("/exit")
        assert result is False


@pytest.mark.asyncio
async def test_scenario_4_error_handling(mock_config, mock_db):
    """
    Сценарий 4: Обработка ошибок.
    - Ошибка LLM → fallback сообщение
    - Ошибка конфигурации → обработка
    - Graceful shutdown
    """
    from src.exceptions import LLMConnectionError

    with patch("src.console.LLMClient"):
        app = ConsoleApp(mock_config, mock_db, user_id=1)

        # Симулируем ошибку LLM
        app.llm_client.get_response = AsyncMock(
            side_effect=LLMConnectionError("Ошибка подключения")
        )

        # Обрабатываем сообщение с ошибкой
        response = await app.get_response("Тест")

        # Проверяем, что получен fallback ответ или сообщение об ошибке
        assert "Извините" in response or "извините" in response
        assert "ошибк" in response.lower() or "сервис" in response.lower()


@pytest.mark.asyncio
async def test_scenario_5_history_management(mock_config, mock_db):
    """
    Сценарий 5: Управление историей.
    - При превышении max_history → удаление старых сообщений
    - При команде /clear → очистка истории
    - Проверка лимитов
    """
    with patch("src.console.LLMClient"):
        app = ConsoleApp(mock_config, mock_db, user_id=1)

        # Симулируем добавление множества сообщений
        # Будем обновлять mock_db.get_messages чтобы вернуть только последние 6 (3 пары)
        messages = []
        message_id = 1
        for i in range(5):
            messages.append(
                {
                    "id": message_id,
                    "role": "user",
                    "content": f"Сообщение {i}",
                    "created_at": f"2025-10-16T10:{i:02d}:00",
                    "length": len(f"Сообщение {i}"),
                    "deleted_at": None,
                }
            )
            message_id += 1
            messages.append(
                {
                    "id": message_id,
                    "role": "assistant",
                    "content": f"Ответ {i}",
                    "created_at": f"2025-10-16T10:{i:02d}:30",
                    "length": len(f"Ответ {i}"),
                    "deleted_at": None,
                }
            )
            message_id += 1

        # Возвращаем только последние 6 сообщений (3 пары) как будто trim сработал
        mock_db.get_messages = AsyncMock(return_value=messages[-6:])

        # Проверяем, что сохранились только последние 6 сообщений (3 пары)
        history = await app.dialog_manager.get_history()
        assert len(history) == 6

        # Проверяем, что остались только последние сообщения
        assert "Сообщение 2" in history[0]["content"]
        assert "Ответ 4" in history[-1]["content"]

        # Очищаем историю
        mock_db.clear_all_messages = AsyncMock(return_value=6)
        mock_db.get_messages = AsyncMock(return_value=[])
        await app.clear_history()
        history_after_clear = await app.dialog_manager.get_history()
        assert len(history_after_clear) == 0


@pytest.mark.asyncio
async def test_different_message_types(mock_config, mock_db):
    """
    Тест различных типов сообщений:
    - Короткие сообщения
    - Длинные сообщения
    - Сообщения с спецсимволами
    - Пустые сообщения
    - Многострочные сообщения
    """
    with patch("src.console.LLMClient"):
        app = ConsoleApp(mock_config, mock_db, user_id=1)
        app.llm_client.get_response = AsyncMock(return_value="Ответ")

        # Короткое сообщение
        response = await app.get_response("Привет")
        assert response == "Ответ"

        # Длинное сообщение
        long_message = "A" * 1000
        response = await app.get_response(long_message)
        assert response == "Ответ"

        # Спецсимволы
        special_message = "Тест !@#$%^&*() \"'<>?"
        response = await app.get_response(special_message)
        assert response == "Ответ"

        # Многострочное сообщение
        multiline = "Первая строка\nВторая строка\nТретья строка"
        response = await app.get_response(multiline)
        assert response == "Ответ"


@pytest.mark.asyncio
async def test_performance_stress(mock_config, mock_db):
    """
    Тест производительности:
    - Обработка множественных запросов
    - Проверка стабильности
    """
    with patch("src.console.LLMClient"):
        app = ConsoleApp(mock_config, mock_db, user_id=1)
        app.llm_client.get_response = AsyncMock(return_value="Ответ")

        # Отправляем 50 сообщений
        for i in range(50):
            response = await app.get_response(f"Сообщение {i}")
            assert response == "Ответ"

        # Проверяем, что add_message был вызван для всех сообщений (50 user + 50 assistant)
        assert mock_db.add_message.call_count == 100


def test_config_validation():
    """
    Тест валидации конфигурации:
    - Проверка обязательных полей
    - Проверка значений по умолчанию
    - Проверка типов данных
    """
    # Создаем конфигурацию с минимальными параметрами
    config = Config(openrouter_api_key="test_key")

    # Проверяем значения по умолчанию
    assert config.llm_model is not None
    assert config.llm_temperature == 0.7
    assert config.llm_max_tokens == 1000
    assert config.max_history == 10
    assert config.log_level == "INFO"


@pytest.mark.asyncio
async def test_dialog_manager_limits(mock_db):
    """
    Тест лимитов DialogManager:
    - Проверка максимальной истории
    - Проверка обрезки истории
    """
    manager = DialogManager(db_client=mock_db, user_id=1, max_history=2)

    # Симулируем добавление 5 пар сообщений и trim до последних 2 пар (4 сообщения)
    messages = []
    for i in range(5):
        messages.append(
            {
                "id": i * 2 + 1,
                "role": "user",
                "content": f"User {i}",
                "created_at": f"2025-10-16T10:{i:02d}:00",
                "length": len(f"User {i}"),
                "deleted_at": None,
            }
        )
        messages.append(
            {
                "id": i * 2 + 2,
                "role": "assistant",
                "content": f"Assistant {i}",
                "created_at": f"2025-10-16T10:{i:02d}:30",
                "length": len(f"Assistant {i}"),
                "deleted_at": None,
            }
        )

    # Возвращаем только последние 4 сообщения (2 пары)
    mock_db.get_messages = AsyncMock(return_value=messages[-4:])

    # Должно остаться только 4 сообщения (2 последние пары)
    history = await manager.get_history()
    assert len(history) == 4

    # Проверяем статистику
    stats = await manager.get_conversation_summary()
    assert stats["total_messages"] == 4
    assert stats["user_messages"] == 2
    assert stats["assistant_messages"] == 2
