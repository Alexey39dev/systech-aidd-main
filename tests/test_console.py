"""Тесты для ConsoleApp."""

from io import StringIO
from unittest.mock import Mock, patch

import pytest

from src.config import Config
from src.console import ConsoleApp
from src.dialog_manager import DialogManager


@pytest.fixture
def mock_config():
    """Создание мок-конфигурации для тестов."""
    config = Mock(spec=Config)
    config.openrouter_api_key = "test_key"
    config.system_prompt = "Test prompt"
    config.max_history = 5
    config.llm_model = "test/model"
    config.llm_temperature = 0.7
    config.llm_max_tokens = 100
    config.log_level = "INFO"
    return config


@pytest.fixture
def console_app(mock_config):
    """Создание экземпляра ConsoleApp для тестов."""
    with patch("src.console.LLMClient"):
        app = ConsoleApp(mock_config)
        return app


def test_console_app_initialization(console_app):
    """Тест инициализации ConsoleApp."""
    assert console_app.config is not None
    assert console_app.dialog_manager is not None
    assert console_app.is_running is False
    assert isinstance(console_app.dialog_manager, DialogManager)


def test_clear_history(console_app):
    """Тест очистки истории."""
    console_app.dialog_manager.add_user_message("Test message")
    assert console_app.dialog_manager.get_history_length() == 1

    console_app.clear_history()
    assert console_app.dialog_manager.get_history_length() == 0


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


def test_print_history_empty(console_app):
    """Тест вывода пустой истории."""
    with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        console_app.print_history()
        output = mock_stdout.getvalue()

        assert "История диалога пуста" in output


def test_print_history_with_messages(console_app):
    """Тест вывода истории с сообщениями."""
    console_app.dialog_manager.add_user_message("Привет!")
    console_app.dialog_manager.add_assistant_message("Здравствуйте!")
    console_app.dialog_manager.add_user_message("Как дела?")

    with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        console_app.print_history()
        output = mock_stdout.getvalue()

        assert "История диалога:" in output
        assert "Вы: Привет!" in output
        assert "Ассистент: Здравствуйте!" in output
        assert "Вы: Как дела?" in output
        assert "Всего сообщений: 3" in output


def test_print_history_truncates_long_messages(console_app):
    """Тест обрезки длинных сообщений в истории."""
    long_message = "A" * 150  # Сообщение длиннее 100 символов
    console_app.dialog_manager.add_user_message(long_message)

    with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        console_app.print_history()
        output = mock_stdout.getvalue()

        assert "..." in output
        assert len(long_message) > 100  # Проверяем, что исходное сообщение длинное


def test_print_stats_empty(console_app):
    """Тест вывода статистики для пустого диалога."""
    with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        console_app.print_stats()
        output = mock_stdout.getvalue()

        assert "Статистика диалога:" in output
        assert "Всего сообщений: 0" in output
        assert "Ваших сообщений: 0" in output
        assert "Ответов ассистента: 0" in output
        assert "Заполнено: 0.0%" in output


def test_print_stats_with_messages(console_app):
    """Тест вывода статистики с сообщениями."""
    console_app.dialog_manager.add_user_message("Тест 1")
    console_app.dialog_manager.add_assistant_message("Ответ 1")
    console_app.dialog_manager.add_user_message("Тест 2")
    console_app.dialog_manager.add_assistant_message("Ответ 2")

    with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        console_app.print_stats()
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
async def test_handle_command_history(console_app):
    """Тест команды /history."""
    console_app.dialog_manager.add_user_message("Test")

    with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        result = await console_app.handle_command("/history")
        output = mock_stdout.getvalue()

        assert result is True
        assert "История диалога:" in output


@pytest.mark.asyncio
async def test_handle_command_stats(console_app):
    """Тест команды /stats."""
    with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        result = await console_app.handle_command("/stats")
        output = mock_stdout.getvalue()

        assert result is True
        assert "Статистика диалога:" in output


@pytest.mark.asyncio
async def test_handle_command_clear(console_app):
    """Тест команды /clear."""
    console_app.dialog_manager.add_user_message("Test 1")
    console_app.dialog_manager.add_assistant_message("Answer 1")

    with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        result = await console_app.handle_command("/clear")
        output = mock_stdout.getvalue()

        assert result is True
        assert "История диалога очищена" in output
        assert "удалено сообщений: 2" in output
        assert console_app.dialog_manager.get_history_length() == 0


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
async def test_get_response_success(console_app):
    """Тест успешного получения ответа от LLM."""
    from unittest.mock import AsyncMock

    # Мокаем успешный ответ
    console_app.llm_client.get_response = AsyncMock(return_value="Test response")

    response = await console_app.get_response("Test question")

    assert response == "Test response"
    assert console_app.dialog_manager.get_history_length() == 2  # user + assistant
    # Проверяем содержимое истории
    history = console_app.dialog_manager.get_history()
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Test question"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "Test response"


@pytest.mark.asyncio
async def test_get_response_llm_error_with_fallback(console_app):
    """Тест обработки LLMError с успешным fallback."""
    from unittest.mock import AsyncMock

    from src.exceptions import LLMConnectionError

    console_app.llm_client.get_response = AsyncMock(
        side_effect=LLMConnectionError("Connection failed")
    )
    console_app.llm_client.get_fallback_response = AsyncMock(return_value="Fallback response")

    response = await console_app.get_response("Test")

    assert response == "Fallback response"
    # История не должна добавляться при ошибке
    assert console_app.dialog_manager.get_history_length() == 0


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
async def test_get_response_with_history(console_app):
    """Тест что get_response использует историю диалога."""
    from unittest.mock import AsyncMock

    # Добавляем предыдущую историю
    console_app.dialog_manager.add_user_message("Previous question")
    console_app.dialog_manager.add_assistant_message("Previous answer")

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
async def test_run_empty_input(console_app):
    """Тест обработки пустого ввода."""
    # Пустой ввод игнорируется, затем выход
    with (
        patch("builtins.input", side_effect=["", "   ", "/exit"]),
        patch("sys.stdout", new_callable=StringIO),
    ):
        await console_app.run()

    assert console_app.dialog_manager.get_history_length() == 0


@pytest.mark.asyncio
async def test_run_with_user_message(console_app):
    """Тест обработки обычного сообщения пользователя."""
    from unittest.mock import AsyncMock

    console_app.llm_client.get_response = AsyncMock(return_value="Response")

    with (
        patch("builtins.input", side_effect=["Hello", "/exit"]),
        patch("sys.stdout", new_callable=StringIO),
    ):
        await console_app.run()

    assert console_app.dialog_manager.get_history_length() == 2


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
