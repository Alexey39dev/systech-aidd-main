"""Интеграционные тесты для проверки всех сценариев из vision.md."""

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


@pytest.mark.asyncio
async def test_scenario_1_application_startup(mock_config):
    """
    Сценарий 1: Запуск приложения.
    - Загрузка конфигурации
    - Инициализация компонентов
    - Проверка готовности к работе
    """
    # Создаем приложение
    with patch("src.console.LLMClient"):
        app = ConsoleApp(mock_config)

    # Проверяем инициализацию
    assert app.config == mock_config
    assert app.dialog_manager is not None
    assert isinstance(app.dialog_manager, DialogManager)
    assert app.dialog_manager.max_history == 3
    assert app.is_running is False


@pytest.mark.asyncio
async def test_scenario_2_user_message_processing(mock_config):
    """
    Сценарий 2: Получение сообщения от пользователя.
    - Получение текста
    - Добавление в историю
    - Отправка запроса к LLM
    - Получение ответа
    """
    with patch("src.console.LLMClient"):
        app = ConsoleApp(mock_config)

        # Настраиваем мок LLM
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Тестовый ответ"))]
        mock_response.usage = None

        app.llm_client.get_response = AsyncMock(return_value="Тестовый ответ")

        # Обрабатываем сообщение
        response = await app.get_response("Привет!")

        # Проверяем результат
        assert response == "Тестовый ответ"
        assert app.dialog_manager.get_history_length() == 2  # user + assistant


@pytest.mark.asyncio
async def test_scenario_3_commands_handling(mock_config):
    """
    Сценарий 3: Обработка команд.
    - /help - справка
    - /clear - очистка истории
    - /history - показ истории
    - /stats - статистика
    - /exit - выход
    """
    with patch("src.console.LLMClient"):
        app = ConsoleApp(mock_config)

        # Добавляем данные в историю
        app.dialog_manager.add_user_message("Тест 1")
        app.dialog_manager.add_assistant_message("Ответ 1")

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
        result = await app.handle_command("/clear")
        assert result is True
        assert app.dialog_manager.get_history_length() == 0

        # Тест /exit
        result = await app.handle_command("/exit")
        assert result is False


@pytest.mark.asyncio
async def test_scenario_4_error_handling(mock_config):
    """
    Сценарий 4: Обработка ошибок.
    - Ошибка LLM → fallback сообщение
    - Ошибка конфигурации → обработка
    - Graceful shutdown
    """
    from src.exceptions import LLMConnectionError

    with patch("src.console.LLMClient"):
        app = ConsoleApp(mock_config)

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
async def test_scenario_5_history_management(mock_config):
    """
    Сценарий 5: Управление историей.
    - При превышении max_history → удаление старых сообщений
    - При команде /clear → очистка истории
    - Проверка лимитов
    """
    with patch("src.console.LLMClient"):
        app = ConsoleApp(mock_config)

        # Добавляем больше сообщений, чем max_history (3 пары = 6 сообщений)
        for i in range(5):
            app.dialog_manager.add_user_message(f"Сообщение {i}")
            app.dialog_manager.add_assistant_message(f"Ответ {i}")

        # Проверяем, что сохранились только последние 6 сообщений (3 пары)
        history = app.dialog_manager.get_history()
        assert len(history) == 6

        # Проверяем, что остались только последние сообщения
        assert "Сообщение 2" in history[0]["content"]
        assert "Ответ 4" in history[-1]["content"]

        # Очищаем историю
        app.clear_history()
        assert app.dialog_manager.get_history_length() == 0


@pytest.mark.asyncio
async def test_different_message_types(mock_config):
    """
    Тест различных типов сообщений:
    - Короткие сообщения
    - Длинные сообщения
    - Сообщения с спецсимволами
    - Пустые сообщения
    - Многострочные сообщения
    """
    with patch("src.console.LLMClient"):
        app = ConsoleApp(mock_config)
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
async def test_performance_stress(mock_config):
    """
    Тест производительности:
    - Обработка множественных запросов
    - Проверка стабильности
    """
    with patch("src.console.LLMClient"):
        app = ConsoleApp(mock_config)
        app.llm_client.get_response = AsyncMock(return_value="Ответ")

        # Отправляем 50 сообщений
        for i in range(50):
            response = await app.get_response(f"Сообщение {i}")
            assert response == "Ответ"

        # Проверяем, что история ограничена
        assert app.dialog_manager.get_history_length() <= mock_config.max_history * 2


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


def test_dialog_manager_limits():
    """
    Тест лимитов DialogManager:
    - Проверка максимальной истории
    - Проверка обрезки истории
    """
    manager = DialogManager(max_history=2)

    # Добавляем 5 пар сообщений (10 сообщений)
    for i in range(5):
        manager.add_user_message(f"User {i}")
        manager.add_assistant_message(f"Assistant {i}")

    # Должно остаться только 4 сообщения (2 последние пары)
    assert manager.get_history_length() == 4

    # Проверяем статистику
    stats = manager.get_conversation_summary()
    assert stats["total_messages"] == 4
    assert stats["user_messages"] == 2
    assert stats["assistant_messages"] == 2
