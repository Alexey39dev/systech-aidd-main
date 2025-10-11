"""Тесты для модуля логирования."""

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock

import structlog

from src.logger import (
    LogColors,
    add_colors_to_console,
    get_logger,
    log_config_info,
    readable_console_renderer,
    setup_logging,
)


def test_add_colors_to_console_debug():
    """Тест добавления цветов для уровня DEBUG."""
    event_dict = {"level": "debug", "event": "test"}
    result = add_colors_to_console(Mock(), "method", event_dict)

    assert "level" in result
    assert LogColors.DEBUG in result["level"]
    assert "DEBUG" in result["level"]


def test_add_colors_to_console_info():
    """Тест добавления цветов для уровня INFO."""
    event_dict = {"level": "info", "event": "test"}
    result = add_colors_to_console(Mock(), "method", event_dict)

    assert LogColors.INFO in result["level"]
    assert "INFO" in result["level"]


def test_add_colors_to_console_warning():
    """Тест добавления цветов для уровня WARNING."""
    event_dict = {"level": "warning", "event": "test"}
    result = add_colors_to_console(Mock(), "method", event_dict)

    assert LogColors.WARNING in result["level"]
    assert "WARNING" in result["level"]


def test_add_colors_to_console_error():
    """Тест добавления цветов для уровня ERROR."""
    event_dict = {"level": "error", "event": "test"}
    result = add_colors_to_console(Mock(), "method", event_dict)

    assert LogColors.ERROR in result["level"]
    assert "ERROR" in result["level"]


def test_add_colors_to_console_unknown_level():
    """Тест обработки неизвестного уровня."""
    event_dict = {"level": "unknown", "event": "test"}
    result = add_colors_to_console(Mock(), "method", event_dict)

    assert "UNKNOWN" in result["level"]


def test_readable_console_renderer_basic():
    """Тест базового рендеринга логов."""
    event_dict = {
        "timestamp": "2025-10-11 12:00:00",
        "level": "INFO",
        "logger": "test_logger",
        "event": "Test message",
    }

    result = readable_console_renderer(Mock(), "method", event_dict)

    assert "2025-10-11 12:00:00" in result
    assert "INFO" in result
    assert "test_logger" in result
    assert "Test message" in result


def test_readable_console_renderer_with_context():
    """Тест рендеринга логов с контекстными полями."""
    event_dict = {
        "timestamp": "2025-10-11 12:00:00",
        "level": "INFO",
        "logger": "test_logger",
        "event": "Test message",
        "user_id": 123,
        "action": "login",
    }

    result = readable_console_renderer(Mock(), "method", event_dict)

    assert "user_id=123" in result
    assert "action=login" in result


def test_readable_console_renderer_missing_fields():
    """Тест рендеринга логов с отсутствующими полями."""
    event_dict = {"event": "Test message"}

    result = readable_console_renderer(Mock(), "method", event_dict)

    assert "Test message" in result
    assert "unknown" in result  # Дефолтный logger


def test_setup_logging_default():
    """Тест базовой настройки логирования."""
    # Сбрасываем состояние
    structlog.reset_defaults()

    setup_logging()

    # Проверяем что логгер создается
    logger = get_logger("test")
    assert logger is not None


def test_setup_logging_with_file_output():
    """Тест настройки логирования с выводом в файл."""
    with TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "test.log"

        structlog.reset_defaults()
        setup_logging(log_level="DEBUG", file_output=str(log_file))

        logger = get_logger("test")
        logger.info("Test log message")

        # Проверяем что файл создан
        assert log_file.exists()


def test_setup_logging_with_console_output():
    """Тест настройки логирования с консольным выводом."""
    structlog.reset_defaults()
    setup_logging(log_level="INFO", console_output=True)

    logger = get_logger("test")
    assert logger is not None


def test_setup_logging_colorful():
    """Тест настройки цветного логирования."""
    structlog.reset_defaults()
    setup_logging(log_level="INFO", console_output=True, colorful=True)

    logger = get_logger("test")
    assert logger is not None


def test_get_logger():
    """Тест получения логгера."""
    structlog.reset_defaults()
    setup_logging()

    logger = get_logger("test_logger")

    assert logger is not None
    # Проверяем что можно вызывать методы логирования
    assert hasattr(logger, "info")
    assert hasattr(logger, "error")
    assert hasattr(logger, "warning")
    assert hasattr(logger, "debug")


def test_log_config_info():
    """Тест логирования информации о конфигурации."""
    from src.config import Config

    structlog.reset_defaults()
    setup_logging()

    # Создаем мок конфигурации
    config = Mock(spec=Config)
    config.system_prompt = "Test system prompt that is quite long to test truncation"
    config.max_history = 10
    config.llm_model = "test/model"
    config.llm_temperature = 0.7
    config.llm_max_tokens = 1000
    config.log_level = "INFO"

    # Просто проверяем что функция выполняется без ошибок
    log_config_info(config)


def test_log_colors_constants():
    """Тест что константы цветов определены."""
    assert hasattr(LogColors, "DEBUG")
    assert hasattr(LogColors, "INFO")
    assert hasattr(LogColors, "WARNING")
    assert hasattr(LogColors, "ERROR")
    assert hasattr(LogColors, "CRITICAL")
    assert hasattr(LogColors, "RESET")
    assert hasattr(LogColors, "TIMESTAMP")
    assert hasattr(LogColors, "LOGGER")
