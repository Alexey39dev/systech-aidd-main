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


def test_config_with_prompt_file(tmp_path):
    """Тест Config с указанием файла промпта."""
    # Arrange
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("# Title: Test\nYou are an assistant.", encoding="utf-8")

    # Act
    config = Config(openrouter_api_key="test", system_prompt_file=str(prompt_file))

    # Assert
    assert config.system_prompt_file == str(prompt_file)


def test_config_prompt_file_optional():
    """Тест что system_prompt_file опционален."""
    # Act
    config = Config(openrouter_api_key="test")

    # Assert
    assert config.system_prompt_file is None


def test_config_validates_file_path(tmp_path):
    """Тест валидации пути к файлу промпта."""
    # Arrange
    non_existent_file = tmp_path / "nonexistent.txt"

    # Act & Assert - должна быть ошибка валидации
    with pytest.raises(ValueError, match="Prompt file not found"):
        Config(openrouter_api_key="test", system_prompt_file=str(non_existent_file))
