"""Тесты для ConsoleApp."""

import pytest
from io import StringIO
from unittest.mock import Mock, patch
from src.console import ConsoleApp
from src.config import Config
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
    with patch('src.console.LLMClient'):
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
    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
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
    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        console_app.print_help()
        output = mock_stdout.getvalue()
        
        assert "Справка по командам" in output
        assert "/help" in output
        assert "/history" in output
        assert "/stats" in output
        assert "/clear" in output
        assert "/exit" in output
        assert "Примеры использования" in output
        assert "Текущая конфигурация" in output
        assert "test/model" in output


def test_print_history_empty(console_app):
    """Тест вывода пустой истории."""
    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        console_app.print_history()
        output = mock_stdout.getvalue()
        
        assert "История диалога пуста" in output


def test_print_history_with_messages(console_app):
    """Тест вывода истории с сообщениями."""
    console_app.dialog_manager.add_user_message("Привет!")
    console_app.dialog_manager.add_assistant_message("Здравствуйте!")
    console_app.dialog_manager.add_user_message("Как дела?")
    
    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
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
    
    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        console_app.print_history()
        output = mock_stdout.getvalue()
        
        assert "..." in output
        assert len(long_message) > 100  # Проверяем, что исходное сообщение длинное


def test_print_stats_empty(console_app):
    """Тест вывода статистики для пустого диалога."""
    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        console_app.print_stats()
        output = mock_stdout.getvalue()
        
        assert "Статистика диалога:" in output
        assert "Всего сообщений: 0" in output
        assert "Ваших сообщений: 0" in output
        assert "Ответов ассистента: 0" in output
        assert "Заполненность истории: 0.0%" in output


def test_print_stats_with_messages(console_app):
    """Тест вывода статистики с сообщениями."""
    console_app.dialog_manager.add_user_message("Тест 1")
    console_app.dialog_manager.add_assistant_message("Ответ 1")
    console_app.dialog_manager.add_user_message("Тест 2")
    console_app.dialog_manager.add_assistant_message("Ответ 2")
    
    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        console_app.print_stats()
        output = mock_stdout.getvalue()
        
        assert "Всего сообщений: 4" in output
        assert "Ваших сообщений: 2" in output
        assert "Ответов ассистента: 2" in output
        assert "Макс. история (пар): 5" in output
        # 4 сообщения из максимум 10 (5 пар) = 40%
        assert "Заполненность истории: 40.0%" in output


@pytest.mark.asyncio
async def test_handle_command_exit(console_app):
    """Тест команды /exit."""
    result = await console_app.handle_command("/exit")
    assert result is False


@pytest.mark.asyncio
async def test_handle_command_help(console_app):
    """Тест команды /help."""
    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        result = await console_app.handle_command("/help")
        output = mock_stdout.getvalue()
        
        assert result is True
        assert "Справка по командам" in output


@pytest.mark.asyncio
async def test_handle_command_history(console_app):
    """Тест команды /history."""
    console_app.dialog_manager.add_user_message("Test")
    
    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        result = await console_app.handle_command("/history")
        output = mock_stdout.getvalue()
        
        assert result is True
        assert "История диалога:" in output


@pytest.mark.asyncio
async def test_handle_command_stats(console_app):
    """Тест команды /stats."""
    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        result = await console_app.handle_command("/stats")
        output = mock_stdout.getvalue()
        
        assert result is True
        assert "Статистика диалога:" in output


@pytest.mark.asyncio
async def test_handle_command_clear(console_app):
    """Тест команды /clear."""
    console_app.dialog_manager.add_user_message("Test 1")
    console_app.dialog_manager.add_assistant_message("Answer 1")
    
    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        result = await console_app.handle_command("/clear")
        output = mock_stdout.getvalue()
        
        assert result is True
        assert "История диалога очищена" in output
        assert "удалено сообщений: 2" in output
        assert console_app.dialog_manager.get_history_length() == 0


@pytest.mark.asyncio
async def test_handle_command_unknown(console_app):
    """Тест неизвестной команды."""
    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        result = await console_app.handle_command("/unknown")
        output = mock_stdout.getvalue()
        
        assert result is True
        assert "Неизвестная команда" in output
        assert "/help" in output


@pytest.mark.asyncio
async def test_handle_command_case_insensitive(console_app):
    """Тест нечувствительности команд к регистру."""
    with patch('sys.stdout', new_callable=StringIO):
        result_lower = await console_app.handle_command("/exit")
        assert result_lower is False
        
        result_upper = await console_app.handle_command("/EXIT")
        assert result_upper is False
        
        result_mixed = await console_app.handle_command("/ExIt")
        assert result_mixed is False

