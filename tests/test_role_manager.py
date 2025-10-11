"""Tests for RoleManager."""

from pathlib import Path

import pytest

from src.role_manager import RoleManager


def test_role_manager_load_from_file(tmp_path: Path) -> None:
    """Тест загрузки промпта из файла."""
    # Arrange
    prompt_file = tmp_path / "test_prompt.txt"
    prompt_file.write_text(
        "# Title: Test Role\n# Description: A test role\n\nYou are a helpful assistant."
    )

    # Act
    manager = RoleManager(prompt_file)

    # Assert
    assert manager.prompt_content != ""
    assert "helpful assistant" in manager.prompt_content


def test_role_manager_parse_metadata() -> None:
    """Тест парсинга метаданных из промпта."""
    # Arrange
    content = """# Title: Tech Support Assistant
# Description: Provides technical support and troubleshooting help.

You are a technical support assistant..."""

    manager = RoleManager()

    # Act
    metadata = manager.parse_metadata(content)

    # Assert
    assert metadata["title"] == "Tech Support Assistant"
    assert "technical support" in metadata["description"]


def test_role_manager_get_role_info(tmp_path: Path) -> None:
    """Тест получения информации о роли."""
    # Arrange
    prompt_file = tmp_path / "role.txt"
    prompt_file.write_text(
        "# Title: Assistant\n# Description: Helpful AI assistant\n\nYou help users."
    )

    # Act
    manager = RoleManager(prompt_file)
    role_info = manager.get_role_info()

    # Assert
    assert role_info["title"] == "Assistant"
    assert role_info["description"] == "Helpful AI assistant"
    assert role_info["source"] == str(prompt_file)


def test_role_manager_file_not_found() -> None:
    """Тест обработки несуществующего файла."""
    # Arrange
    non_existent_file = Path("/path/to/nonexistent/file.txt")

    # Act & Assert
    with pytest.raises(FileNotFoundError):
        RoleManager(non_existent_file)


def test_role_manager_empty_file(tmp_path: Path) -> None:
    """Тест обработки пустого файла."""
    # Arrange
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("")

    # Act
    manager = RoleManager(empty_file)
    role_info = manager.get_role_info()

    # Assert - должен быть fallback
    assert role_info["title"] == "Custom Role"
    assert role_info["description"] == "Loaded from file"


def test_role_manager_no_metadata(tmp_path: Path) -> None:
    """Тест промпта без метаданных."""
    # Arrange
    prompt_file = tmp_path / "no_metadata.txt"
    prompt_file.write_text("You are a helpful assistant without metadata.")

    # Act
    manager = RoleManager(prompt_file)
    role_info = manager.get_role_info()

    # Assert - должен быть fallback
    assert role_info["title"] == "Custom Role"
    assert role_info["description"] == "Loaded from file"
    assert role_info["source"] == str(prompt_file)


def test_role_manager_without_file() -> None:
    """Тест RoleManager без файла (default роль)."""
    # Act
    manager = RoleManager()
    role_info = manager.get_role_info()

    # Assert - должна быть default роль
    assert role_info["title"] == "Default Role"
    assert role_info["description"] == "No role file specified"
    assert role_info["source"] == "default"


def test_role_manager_multiline_description(tmp_path: Path) -> None:
    """Тест многострочного описания."""
    # Arrange
    prompt_file = tmp_path / "multiline.txt"
    prompt_file.write_text(
        "# Title: Complex Role\n"
        "# Description: First line\n"
        "# Second line of description\n"
        "\n"
        "You are complex."
    )

    # Act
    manager = RoleManager(prompt_file)
    role_info = manager.get_role_info()

    # Assert
    assert role_info["title"] == "Complex Role"
    assert "First line" in role_info["description"]
    assert "Second line" in role_info["description"]


def test_role_manager_with_unicode(tmp_path: Path) -> None:
    """Тест Unicode в метаданных."""
    # Arrange
    prompt_file = tmp_path / "unicode.txt"
    prompt_file.write_text(
        "# Title: Русский Ассистент\n"
        "# Description: Помощник с поддержкой 中文 и emoji 🤖\n"
        "\n"
        "Вы помогаете пользователям.",
        encoding="utf-8",
    )

    # Act
    manager = RoleManager(prompt_file)
    role_info = manager.get_role_info()

    # Assert
    assert role_info["title"] == "Русский Ассистент"
    assert "🤖" in role_info["description"]
    assert "中文" in role_info["description"]
