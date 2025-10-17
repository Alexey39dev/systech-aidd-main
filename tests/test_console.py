"""Тесты для ConsoleApp."""

from datetime import datetime
from io import StringIO
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.config import Config
from src.console import ConsoleApp
from src.database import DatabaseClient
from src.dialog_manager import DialogManager


@pytest.fixture
def mock_config():
    """Создание мок-конфигурации для тестов."""
    config = Mock(spec=Config)
    config.openrouter_api_key = "test_key"
    config.system_prompt = "Test prompt"
    config.system_prompt_file = None
    config.max_history = 5
    config.llm_model = "test/model"
    config.llm_temperature = 0.7
    config.llm_max_tokens = 100
    config.log_level = "INFO"
    return config


@pytest.fixture
def mock_db():
    """Создание мок-клиента БД для тестов."""
    db = AsyncMock(spec=DatabaseClient)
    db.add_message = AsyncMock(return_value=(1, datetime(2025, 10, 16, 10, 0, 0)))
    db.get_messages = AsyncMock(return_value=[])
    db.clear_all_messages = AsyncMock(return_value=0)
    db.soft_delete_message = AsyncMock()
    return db


@pytest.fixture
def console_app(mock_config, mock_db):
    """Создание экземпляра ConsoleApp для тестов."""
    with patch("src.console.LLMClient"):
        app = ConsoleApp(mock_config, mock_db, user_id=1)
        return app


def test_console_app_initialization(console_app):
    """Тест инициализации ConsoleApp."""
    assert console_app.config is not None
    assert console_app.dialog_manager is not None
    assert console_app.is_running is False
    assert isinstance(console_app.dialog_manager, DialogManager)


@pytest.mark.asyncio
async def test_clear_history(console_app, mock_db):
    """Тест очистки истории."""
    mock_db.clear_all_messages = AsyncMock(return_value=1)
    mock_db.get_messages = AsyncMock(return_value=[])

    await console_app.clear_history()
    mock_db.clear_all_messages.assert_called_once()


def test_print_welcome(console_app):
    """Тест вывода приветственного сообщения."""
    with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        console_app.print_welcome()
        output = mock_stdout.getvalue()

        assert "LLM-Ассистент через консоль" in output
        assert "/help" in output
        assert "/history" in output
        assert "/stats" in output
        assert "/clear" in output
        assert "/exit" in output


def test_print_help(console_app):
    """Тест вывода справки."""
    with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        console_app.print_help()
        output = mock_stdout.getvalue()

        assert "Справка по командам" in output
        assert "/help" in output
        assert "/history" in output
        assert "/stats" in output
        assert "/clear" in output
        assert "/exit" in output
        assert "Примеры вопросов" in output
        assert "Текущие настройки" in output
        assert "test/model" in output


@pytest.mark.asyncio
async def test_print_history_empty(console_app, mock_db):
    """Тест вывода пустой истории."""
    mock_db.get_messages = AsyncMock(return_value=[])

    with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        await console_app.print_history()
        output = mock_stdout.getvalue()

        assert "История диалога пуста" in output


@pytest.mark.asyncio
async def test_print_history_with_messages(console_app, mock_db):
    """Тест вывода истории с сообщениями."""
    mock_db.get_messages = AsyncMock(
        return_value=[
            {
                "id": 1,
                "role": "user",
                "content": "Привет!",
                "created_at": "2025-10-16T10:00:00",
                "length": 7,
                "deleted_at": None,
            },
            {
                "id": 2,
                "role": "assistant",
                "content": "Здравствуйте!",
                "created_at": "2025-10-16T10:01:00",
                "length": 13,
                "deleted_at": None,
            },
            {
                "id": 3,
                "role": "user",
                "content": "Как дела?",
                "created_at": "2025-10-16T10:02:00",
                "length": 9,
                "deleted_at": None,
            },
        ]
    )

    with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        await console_app.print_history()
        output = mock_stdout.getvalue()

        assert "История диалога:" in output
        assert "Вы: Привет!" in output
        assert "Ассистент: Здравствуйте!" in output
        assert "Вы: Как дела?" in output
        assert "Всего сообщений: 3" in output


@pytest.mark.asyncio
async def test_print_history_truncates_long_messages(console_app, mock_db):
    """Тест обрезки длинных сообщений в истории."""
    long_message = "A" * 150  # Сообщение длиннее 100 символов
    mock_db.get_messages = AsyncMock(
        return_value=[
            {
                "id": 1,
                "role": "user",
                "content": long_message,
                "created_at": "2025-10-16T10:00:00",
                "length": 150,
                "deleted_at": None,
            }
        ]
    )

    with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        await console_app.print_history()
        output = mock_stdout.getvalue()

        assert "..." in output
        assert len(long_message) > 100  # Проверяем, что исходное сообщение длинное


@pytest.mark.asyncio
async def test_print_stats_empty(console_app, mock_db):
    """Тест вывода статистики для пустого диалога."""
    mock_db.get_messages = AsyncMock(return_value=[])

    with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        await console_app.print_stats()
        output = mock_stdout.getvalue()

        assert "Статистика диалога:" in output
        assert "Всего сообщений: 0" in output
        assert "Ваших сообщений: 0" in output
        assert "Ответов ассистента: 0" in output
        assert "Заполнено: 0.0%" in output


@pytest.mark.asyncio
async def test_print_stats_with_messages(console_app, mock_db):
    """Тест вывода статистики с сообщениями."""
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
            {
                "id": 3,
                "role": "user",
                "content": "Тест 2",
                "created_at": "2025-10-16T10:02:00",
                "length": 6,
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

    with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        await console_app.print_stats()
        output = mock_stdout.getvalue()

        assert "Всего сообщений: 4" in output
        assert "Ваших сообщений: 2" in output
        assert "Ответов ассистента: 2" in output
        assert "Макс. история (пар): 5" in output
        # 2 пары из максимум 5 пар = 40%
        assert "Заполнено: 40.0%" in output


@pytest.mark.asyncio
async def test_handle_command_exit(console_app):
    """Тест команды /exit."""
    result = await console_app.handle_command("/exit")
    assert result is False


@pytest.mark.asyncio
async def test_handle_command_help(console_app):
    """Тест команды /help."""
    with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        result = await console_app.handle_command("/help")
        output = mock_stdout.getvalue()

        assert result is True
        assert "Справка по командам" in output


@pytest.mark.asyncio
async def test_handle_command_history(console_app, mock_db):
    """Тест команды /history."""
    mock_db.get_messages = AsyncMock(
        return_value=[
            {
                "id": 1,
                "role": "user",
                "content": "Test",
                "created_at": "2025-10-16T10:00:00",
                "length": 4,
                "deleted_at": None,
            }
        ]
    )

    with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        result = await console_app.handle_command("/history")
        output = mock_stdout.getvalue()

        assert result is True
        assert "История диалога:" in output


@pytest.mark.asyncio
async def test_handle_command_stats(console_app, mock_db):
    """Тест команды /stats."""
    mock_db.get_messages = AsyncMock(return_value=[])

    with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        result = await console_app.handle_command("/stats")
        output = mock_stdout.getvalue()

        assert result is True
        assert "Статистика диалога:" in output


@pytest.mark.asyncio
async def test_handle_command_clear(console_app, mock_db):
    """Тест команды /clear."""
    mock_db.get_messages = AsyncMock(
        return_value=[
            {
                "id": 1,
                "role": "user",
                "content": "Test 1",
                "created_at": "2025-10-16T10:00:00",
                "length": 6,
                "deleted_at": None,
            },
            {
                "id": 2,
                "role": "assistant",
                "content": "Answer 1",
                "created_at": "2025-10-16T10:01:00",
                "length": 8,
                "deleted_at": None,
            },
        ]
    )
    mock_db.clear_all_messages = AsyncMock(return_value=2)

    with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        result = await console_app.handle_command("/clear")
        output = mock_stdout.getvalue()

        assert result is True
        assert "История диалога очищена" in output
        assert "удалено сообщений: 2" in output
        mock_db.clear_all_messages.assert_called_once()


@pytest.mark.asyncio
async def test_handle_command_unknown(console_app):
    """Тест неизвестной команды."""
    with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        result = await console_app.handle_command("/unknown")
        output = mock_stdout.getvalue()

        assert result is True
        assert "Неизвестная команда" in output
        assert "/help" in output


@pytest.mark.asyncio
async def test_handle_command_case_insensitive(console_app):
    """Тест нечувствительности команд к регистру."""
    with patch("sys.stdout", new_callable=StringIO):
        result_lower = await console_app.handle_command("/exit")
        assert result_lower is False

        result_upper = await console_app.handle_command("/EXIT")
        assert result_upper is False

        result_mixed = await console_app.handle_command("/ExIt")
        assert result_mixed is False


# === Тесты для get_response ===


@pytest.mark.asyncio
async def test_get_response_success(console_app, mock_db):
    """Тест успешного получения ответа от LLM."""
    from unittest.mock import AsyncMock

    # Мокаем БД для истории
    mock_db.get_messages = AsyncMock(return_value=[])
    mock_db.add_message = AsyncMock(return_value=(1, datetime(2025, 10, 16, 10, 0, 0)))

    # Мокаем успешный ответ
    console_app.llm_client.get_response = AsyncMock(return_value="Test response")

    response = await console_app.get_response("Test question")

    assert response == "Test response"
    # Проверяем что вызвался add_message для user и assistant
    assert mock_db.add_message.call_count == 2


@pytest.mark.asyncio
async def test_get_response_llm_error_with_fallback(console_app, mock_db):
    """Тест обработки LLMError с успешным fallback."""
    from unittest.mock import AsyncMock

    from src.exceptions import LLMConnectionError

    mock_db.get_messages = AsyncMock(return_value=[])

    console_app.llm_client.get_response = AsyncMock(
        side_effect=LLMConnectionError("Connection failed")
    )
    console_app.llm_client.get_fallback_response = AsyncMock(return_value="Fallback response")

    response = await console_app.get_response("Test")

    assert response == "Fallback response"
    # История не должна добавляться при ошибке
    mock_db.add_message.assert_not_called()


@pytest.mark.asyncio
async def test_get_response_llm_error_fallback_fails(console_app):
    """Тест обработки LLMError когда fallback тоже падает."""
    from unittest.mock import AsyncMock

    from src.exceptions import LLMRateLimitError

    console_app.llm_client.get_response = AsyncMock(
        side_effect=LLMRateLimitError("Rate limit exceeded")
    )
    console_app.llm_client.get_fallback_response = AsyncMock(
        side_effect=Exception("Fallback failed")
    )

    response = await console_app.get_response("Test")

    assert "Извините" in response
    assert "ошибка" in response
    assert "сервису" in response


@pytest.mark.asyncio
async def test_get_response_unexpected_error(console_app):
    """Тест обработки неожиданного исключения."""
    from unittest.mock import AsyncMock

    console_app.llm_client.get_response = AsyncMock(side_effect=RuntimeError("Unexpected error"))

    response = await console_app.get_response("Test")

    assert "Извините" in response
    assert "неожиданная ошибка" in response


@pytest.mark.asyncio
async def test_get_response_keyboard_interrupt(console_app):
    """Тест что KeyboardInterrupt пробрасывается дальше."""
    from unittest.mock import AsyncMock

    console_app.llm_client.get_response = AsyncMock(side_effect=KeyboardInterrupt())

    with pytest.raises(KeyboardInterrupt):
        await console_app.get_response("Test")


@pytest.mark.asyncio
async def test_get_response_with_history(console_app, mock_db):
    """Тест что get_response использует историю диалога."""
    from unittest.mock import AsyncMock

    # Мокаем предыдущую историю
    mock_db.get_messages = AsyncMock(
        return_value=[
            {
                "id": 1,
                "role": "user",
                "content": "Previous question",
                "created_at": "2025-10-16T10:00:00",
                "length": 17,
                "deleted_at": None,
            },
            {
                "id": 2,
                "role": "assistant",
                "content": "Previous answer",
                "created_at": "2025-10-16T10:01:00",
                "length": 15,
                "deleted_at": None,
            },
        ]
    )
    mock_db.add_message = AsyncMock(return_value=(3, datetime(2025, 10, 16, 10, 2, 0)))

    console_app.llm_client.get_response = AsyncMock(return_value="New response")

    await console_app.get_response("New question")

    # Проверяем, что LLM вызывался с историей
    console_app.llm_client.get_response.assert_called_once()
    call_kwargs = console_app.llm_client.get_response.call_args.kwargs
    assert "conversation_history" in call_kwargs
    assert len(call_kwargs["conversation_history"]) == 2


# === Тесты для run() и stop() ===


@pytest.mark.asyncio
async def test_run_with_exit_command(console_app):
    """Тест запуска с выходом через команду /exit."""
    with (
        patch("builtins.input", side_effect=["/exit"]),
        patch("sys.stdout", new_callable=StringIO),
    ):
        await console_app.run()

    assert console_app.is_running is False


@pytest.mark.asyncio
async def test_run_with_keyboard_interrupt(console_app):
    """Тест обработки KeyboardInterrupt в run()."""
    with (
        patch("builtins.input", side_effect=KeyboardInterrupt()),
        patch("sys.stdout", new_callable=StringIO),
    ):
        await console_app.run()

    assert console_app.is_running is False


@pytest.mark.asyncio
async def test_run_with_eof_error(console_app):
    """Тест обработки EOFError в run()."""
    with (
        patch("builtins.input", side_effect=EOFError()),
        patch("sys.stdout", new_callable=StringIO),
    ):
        await console_app.run()

    assert console_app.is_running is False


@pytest.mark.asyncio
async def test_run_empty_input(console_app, mock_db):
    """Тест обработки пустого ввода."""
    mock_db.get_messages = AsyncMock(return_value=[])

    # Пустой ввод игнорируется, затем выход
    with (
        patch("builtins.input", side_effect=["", "   ", "/exit"]),
        patch("sys.stdout", new_callable=StringIO),
    ):
        await console_app.run()

    # Проверяем что add_message не вызывался (пустой ввод игнорируется)
    mock_db.add_message.assert_not_called()


@pytest.mark.asyncio
async def test_run_with_user_message(console_app, mock_db):
    """Тест обработки обычного сообщения пользователя."""
    from unittest.mock import AsyncMock

    mock_db.get_messages = AsyncMock(return_value=[])
    mock_db.add_message = AsyncMock(return_value=(1, datetime(2025, 10, 16, 10, 0, 0)))

    console_app.llm_client.get_response = AsyncMock(return_value="Response")

    with (
        patch("builtins.input", side_effect=["Hello", "/exit"]),
        patch("sys.stdout", new_callable=StringIO),
    ):
        await console_app.run()

    # Проверяем что add_message вызывался для user и assistant
    assert mock_db.add_message.call_count == 2


@pytest.mark.asyncio
async def test_run_with_exception(console_app):
    """Тест обработки критической ошибки в run()."""
    # Мокаем get_event_loop для выброса исключения
    with (
        patch("asyncio.get_event_loop") as mock_loop,
        patch("sys.stdout", new_callable=StringIO),
    ):
        mock_loop.return_value.run_in_executor.side_effect = RuntimeError("Critical error")
        await console_app.run()

    assert console_app.is_running is False


@pytest.mark.asyncio
async def test_stop(console_app):
    """Тест метода stop()."""
    console_app.is_running = True
    await console_app.stop()
    assert console_app.is_running is False


@pytest.mark.asyncio
async def test_stop_when_not_running(console_app):
    """Тест метода stop() когда приложение не запущено."""
    console_app.is_running = False
    await console_app.stop()
    assert console_app.is_running is False


def test_console_role_command(tmp_path, mock_config, mock_db):
    """Тест команды /role отображает информацию о роли."""
    # Arrange
    prompt_file = tmp_path / "role.txt"
    prompt_file.write_text(
        "# Title: Test Assistant\n# Description: A test role\n\nYou are a test.",
        encoding="utf-8",
    )
    mock_config.system_prompt_file = str(prompt_file)

    with patch("src.console.LLMClient"):
        app = ConsoleApp(mock_config, mock_db, user_id=1)

        # Act
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            app.print_role_info()
            output = mock_stdout.getvalue()

            # Assert
            assert "Текущая роль:" in output
            assert "Test Assistant" in output
            assert "A test role" in output


def test_console_role_command_without_file(console_app):
    """Тест команды /role когда файл не указан."""
    # Act
    with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        console_app.print_role_info()
        output = mock_stdout.getvalue()

        # Assert
        assert "Текущая роль:" in output
        assert "Default Role" in output


def test_console_help_includes_role(console_app):
    """Тест что /help содержит информацию о команде /role."""
    # Act
    with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        console_app.print_help()
        output = mock_stdout.getvalue()

        # Assert
        assert "/role" in output
