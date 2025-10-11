"""Тесты для main.py - ApplicationContext и запуск приложения."""

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from src.config import Config
from src.console import ConsoleApp
from src.main import ApplicationContext, create_shutdown_handler


@pytest.fixture
def mock_config():
    """Фикстура для мок-конфигурации."""
    return Config(openrouter_api_key="test_api_key")


@pytest.fixture
def mock_console_app(mock_config):
    """Фикстура для мок-приложения."""
    app = Mock(spec=ConsoleApp)
    app.is_running = True
    app.stop = AsyncMock()
    return app


class TestApplicationContext:
    """Тесты для класса ApplicationContext."""

    def test_context_initialization(self):
        """Тест инициализации контекста."""
        context = ApplicationContext()

        assert context.app is None
        assert context.logger is not None
        assert context._shutdown_event is not None

    def test_set_app(self, mock_console_app):
        """Тест установки приложения в контекст."""
        context = ApplicationContext()
        context.set_app(mock_console_app)

        assert context.app == mock_console_app

    def test_request_shutdown(self, mock_console_app):
        """Тест запроса на остановку."""
        context = ApplicationContext()
        context.set_app(mock_console_app)

        # Проверяем что событие не установлено
        assert not context._shutdown_event.is_set()

        # Запрашиваем остановку
        context.request_shutdown()

        # Проверяем что событие установлено
        assert context._shutdown_event.is_set()

    def test_request_shutdown_without_app(self):
        """Тест запроса на остановку без приложения."""
        context = ApplicationContext()

        # Не должно вызвать ошибку
        context.request_shutdown()

        # Событие не должно быть установлено
        assert not context._shutdown_event.is_set()

    def test_request_shutdown_app_not_running(self, mock_console_app):
        """Тест запроса на остановку когда приложение не запущено."""
        context = ApplicationContext()
        mock_console_app.is_running = False
        context.set_app(mock_console_app)

        context.request_shutdown()

        # Событие не должно быть установлено
        assert not context._shutdown_event.is_set()

    @pytest.mark.asyncio
    async def test_shutdown(self, mock_console_app):
        """Тест асинхронной остановки приложения."""
        context = ApplicationContext()
        context.set_app(mock_console_app)

        await context.shutdown()

        # Проверяем что был вызван stop()
        mock_console_app.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_shutdown_without_app(self):
        """Тест остановки без приложения."""
        context = ApplicationContext()

        # Не должно вызвать ошибку
        await context.shutdown()

    @pytest.mark.asyncio
    async def test_shutdown_app_not_running(self, mock_console_app):
        """Тест остановки когда приложение не запущено."""
        context = ApplicationContext()
        mock_console_app.is_running = False
        context.set_app(mock_console_app)

        await context.shutdown()

        # stop() не должен быть вызван
        mock_console_app.stop.assert_not_called()

    @pytest.mark.asyncio
    async def test_wait_for_shutdown(self, mock_console_app):
        """Тест ожидания сигнала остановки."""
        context = ApplicationContext()
        context.set_app(mock_console_app)

        # Запускаем ожидание в фоне
        wait_task = asyncio.create_task(context.wait_for_shutdown())

        # Даем задаче начать выполнение
        await asyncio.sleep(0.1)

        # Проверяем что задача еще не завершена
        assert not wait_task.done()

        # Запрашиваем остановку
        context.request_shutdown()

        # Ждем завершения задачи
        await asyncio.wait_for(wait_task, timeout=1.0)

        # Проверяем что задача завершена
        assert wait_task.done()

    def test_cleanup(self, mock_console_app):
        """Тест очистки ресурсов."""
        context = ApplicationContext()
        context.set_app(mock_console_app)

        # Проверяем что приложение установлено
        assert context.app is not None

        # Очищаем
        context.cleanup()

        # Проверяем что приложение удалено
        assert context.app is None


class TestShutdownHandler:
    """Тесты для обработчика сигналов завершения."""

    def test_create_shutdown_handler(self, mock_console_app):
        """Тест создания обработчика завершения."""
        context = ApplicationContext()
        context.set_app(mock_console_app)

        handler = create_shutdown_handler(context)

        assert callable(handler)

    def test_shutdown_handler_execution(self, mock_console_app, capsys):
        """Тест выполнения обработчика завершения."""
        context = ApplicationContext()
        context.set_app(mock_console_app)

        handler = create_shutdown_handler(context)

        # Вызываем обработчик
        handler(2, None)  # SIGINT

        # Проверяем что событие установлено
        assert context._shutdown_event.is_set()

        # Проверяем вывод
        captured = capsys.readouterr()
        assert "Получен сигнал завершения" in captured.out
