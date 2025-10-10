"""Настройка логирования для приложения."""

import structlog
import logging
import sys
from typing import Any, Dict


def setup_logging(log_level: str = "INFO") -> None:
    """Настройка структурированного логирования.
    
    Args:
        log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Настройка стандартного logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout
    )
    
    # Настройка structlog
    structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
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
    return structlog.get_logger(name)


def log_config_info(config: Any) -> None:
    """Логирование информации о конфигурации (без секретных данных).
    
    Args:
        config: Объект конфигурации
    """
    logger = get_logger("config")
    logger.info(
        "Конфигурация загружена",
        system_prompt=config.system_prompt[:50] + "..." if len(config.system_prompt) > 50 else config.system_prompt,
        max_history=config.max_history,
        llm_model=config.llm_model,
        llm_temperature=config.llm_temperature,
        llm_max_tokens=config.llm_max_tokens,
        log_level=config.log_level
    )
