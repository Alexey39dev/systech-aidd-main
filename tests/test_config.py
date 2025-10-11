"""Тесты для конфигурации."""

import pytest

from src.config import Config


def test_config_creation():
    """Тест создания конфигурации."""
    # Создаем конфигурацию с тестовыми данными
    config = Config(openrouter_api_key="test_api_key")

    assert config.openrouter_api_key == "test_api_key"
    assert "полезный ассистент" in config.system_prompt.lower()
    assert config.max_history == 10
    # Модель может быть переопределена в .env, проверяем что она задана
    assert config.llm_model is not None
    assert config.llm_temperature == 0.7
    assert config.llm_max_tokens == 1000
    assert config.log_level == "INFO"


def test_config_defaults():
    """Тест значений по умолчанию."""
    config = Config(openrouter_api_key="test_api_key")

    # Проверяем значения по умолчанию
    assert config.max_history == 10
    # Модель может быть переопределена в .env, проверяем что она задана
    assert config.llm_model is not None
    assert config.llm_temperature == 0.7
    assert config.llm_max_tokens == 1000
    assert config.log_level == "INFO"


def test_config_validation():
    """Тест валидации конфигурации."""
    # Тест с невалидными значениями
    with pytest.raises(ValueError):
        Config(
            openrouter_api_key="test_api_key",
            llm_temperature=3.0,  # Должно быть <= 2.0
        )

    with pytest.raises(ValueError):
        Config(
            openrouter_api_key="test_api_key",
            max_history=100,  # Должно быть <= 50
        )
