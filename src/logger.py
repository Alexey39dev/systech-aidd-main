"""Настройка логирования для приложения."""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import TYPE_CHECKING

import structlog
from structlog.types import EventDict, WrappedLogger

if TYPE_CHECKING:
    from .config import Config


# Цвета для разных уровней логирования (ANSI коды)
class LogColors:
    """ANSI коды для цветного вывода."""

    RESET = "\033[0m"
    DEBUG = "\033[36m"  # Cyan
    INFO = "\033[32m"  # Green
    WARNING = "\033[33m"  # Yellow
    ERROR = "\033[31m"  # Red
    CRITICAL = "\033[35m"  # Magenta
    TIMESTAMP = "\033[90m"  # Dark gray
    LOGGER = "\033[94m"  # Light blue


def add_colors_to_console(
    logger: WrappedLogger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Добавляет цвета к консольному выводу."""
    level = event_dict.get("level", "info")
    level = level.upper() if isinstance(level, str) else str(level).upper()

    # Цвет для уровня
    color_map = {
        "DEBUG": LogColors.DEBUG,
        "INFO": LogColors.INFO,
        "WARNING": LogColors.WARNING,
        "ERROR": LogColors.ERROR,
        "CRITICAL": LogColors.CRITICAL,
    }

    level_color = color_map.get(level, LogColors.RESET)

    # Форматируем с цветами
    event_dict["level"] = f"{level_color}{level}{LogColors.RESET}"

    return event_dict


def readable_console_renderer(
    logger: WrappedLogger, method_name: str, event_dict: EventDict
) -> str:
    """Рендерит логи в читаемом формате для консоли."""
    timestamp = event_dict.pop("timestamp", "")
    level = event_dict.pop("level", "INFO")
    logger_name = event_dict.pop("logger", "unknown")
    event = event_dict.pop("event", "")

    # Формируем основное сообщение
    parts = [
        f"{LogColors.TIMESTAMP}{timestamp}{LogColors.RESET}",
        f"[{level}]",
        f"{LogColors.LOGGER}{logger_name}{LogColors.RESET}",
        f"- {event}",
    ]

    message = " ".join(parts)

    # Добавляем контекстные поля
    if event_dict:
        context_parts = []
        for key, value in event_dict.items():
            context_parts.append(f"{key}={value}")

        if context_parts:
            message += f" | {', '.join(context_parts)}"

    return message


def setup_logging(
    log_level: str = "INFO",
    console_output: bool = False,
    file_output: str | None = None,
    colorful: bool = False,
) -> None:
    """Настройка структурированного логирования.

    Args:
        log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console_output: Выводить ли логи в консоль
        file_output: Путь к файлу для логирования (None = не писать в файл)
        colorful: Использовать ли цветной вывод (только для консоли)
    """
    # Настройка стандартного logging
    handlers: list[logging.Handler] = []

    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        handlers.append(console_handler)

    if file_output:
        # Создаём директорию для логов если не существует
        log_path = Path(file_output)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Rotating file handler (макс 10MB, 5 резервных копий)
        file_handler = RotatingFileHandler(
            file_output,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        handlers.append(file_handler)

    if not handlers:
        # Если нет обработчиков, используем NullHandler
        handlers.append(logging.NullHandler())

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )

    # Настройка structlog процессоров
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    # Выбор рендерера в зависимости от режима
    if console_output and colorful:
        processors.append(add_colors_to_console)
        processors.append(readable_console_renderer)
    elif console_output:
        processors.append(readable_console_renderer)
    else:
        # Для файлового вывода используем JSON
        processors.append(structlog.processors.JSONRenderer())

    # Настройка structlog
    structlog.configure(
        processors=processors,  # type: ignore[arg-type]
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Получить логгер с заданным именем.

    Args:
        name: Имя логгера (обычно __name__)

    Returns:
        Настроенный логгер
    """
    return structlog.get_logger(name)  # type: ignore[no-any-return]


def log_config_info(config: "Config") -> None:
    """Логирование информации о конфигурации (без секретных данных).

    Args:
        config: Объект конфигурации (Config)
    """
    logger = get_logger("config")
    logger.info(
        "Конфигурация загружена",
        system_prompt=config.system_prompt[:50] + "..."
        if len(config.system_prompt) > 50
        else config.system_prompt,
        max_history=config.max_history,
        llm_model=config.llm_model,
        llm_temperature=config.llm_temperature,
        llm_max_tokens=config.llm_max_tokens,
        log_level=config.log_level,
    )
