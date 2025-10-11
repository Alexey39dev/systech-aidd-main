"""Role Manager - загрузка и парсинг промптов из файлов."""

import re
from pathlib import Path
from typing import Final, TypedDict


class RoleMetadata(TypedDict):
    """Метаданные роли.

    Attributes:
        title: Название роли
        description: Описание роли
        source: Источник роли (путь к файлу или "default")
    """

    title: str
    description: str
    source: str


# Константы для fallback значений
DEFAULT_ROLE_TITLE: Final[str] = "Default Role"
DEFAULT_ROLE_DESCRIPTION: Final[str] = "No role file specified"
CUSTOM_ROLE_TITLE: Final[str] = "Custom Role"
CUSTOM_ROLE_DESCRIPTION: Final[str] = "Loaded from file"


class RoleManager:
    """Менеджер ролей - загрузка и парсинг промптов из файлов.

    Поддерживает загрузку промптов из файлов с метаданными в формате:
    # Title: Название роли
    # Description: Описание роли (может быть многострочным)

    Examples:
        >>> manager = RoleManager(Path("prompts/default.txt"))
        >>> role_info = manager.get_role_info()
        >>> print(role_info["title"])
        'General Assistant'
    """

    def __init__(self, prompt_file: Path | None = None) -> None:
        """Инициализация RoleManager.

        Args:
            prompt_file: Путь к файлу с промптом (опционально)

        Raises:
            FileNotFoundError: Если указанный файл не существует
        """
        self.prompt_file = prompt_file
        self.prompt_content = ""
        self.metadata: RoleMetadata | None = None

        if prompt_file:
            self._validate_file_exists(prompt_file)
            self.load_prompt_from_file()

    def _validate_file_exists(self, file_path: Path) -> None:
        """Валидация существования файла.

        Args:
            file_path: Путь к файлу для проверки

        Raises:
            FileNotFoundError: Если файл не существует
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {file_path}")

    def load_prompt_from_file(self) -> str:
        """Загрузить промпт из файла.

        Returns:
            Содержимое промпта

        Raises:
            FileNotFoundError: Если файл не найден
        """
        if not self.prompt_file:
            return ""

        self.prompt_content = self.prompt_file.read_text(encoding="utf-8")
        self.metadata = self.parse_metadata(self.prompt_content)
        return self.prompt_content

    def parse_metadata(self, content: str) -> RoleMetadata:
        """Парсинг метаданных из комментариев.

        Формат метаданных в начале файла:
        # Title: Название роли
        # Description: Описание роли
        # Или многострочное описание (несколько строк с #)

        Args:
            content: Содержимое промпта

        Returns:
            Словарь с метаданными (title, description, source)
        """
        title = self._extract_title(content)
        description = self._extract_description(content)
        source = str(self.prompt_file) if self.prompt_file else "default"

        return {"title": title, "description": description, "source": source}

    def _extract_title(self, content: str) -> str:
        """Извлечь заголовок из содержимого.

        Args:
            content: Содержимое промпта

        Returns:
            Название роли или fallback значение
        """
        title_match = re.search(r"^#\s*Title:\s*(.+)$", content, re.MULTILINE)
        return title_match.group(1).strip() if title_match else CUSTOM_ROLE_TITLE

    def _extract_description(self, content: str) -> str:
        """Извлечь описание из содержимого (поддержка многострочного описания).

        Args:
            content: Содержимое промпта

        Returns:
            Описание роли или fallback значение
        """
        description_lines = []

        for line in content.split("\n"):
            if line.startswith("# Description:"):
                # Первая строка описания
                description_lines.append(line.replace("# Description:", "").strip())
            elif line.startswith("#") and description_lines and not line.startswith("# Title:"):
                # Продолжение описания (строки начинающиеся с #)
                desc_part = line.lstrip("#").strip()
                if desc_part:
                    description_lines.append(desc_part)
            elif description_lines and not line.startswith("#"):
                # Закончились строки с метаданными
                break

        return " ".join(description_lines) if description_lines else CUSTOM_ROLE_DESCRIPTION

    def get_role_info(self) -> RoleMetadata:
        """Получить информацию о текущей роли.

        Returns:
            Словарь с метаданными роли (title, description, source)

        Note:
            Если файл не был загружен, возвращает метаданные роли по умолчанию.
        """
        if self.metadata:
            return self.metadata

        # Fallback для случаев без файла
        return {
            "title": DEFAULT_ROLE_TITLE,
            "description": DEFAULT_ROLE_DESCRIPTION,
            "source": "default",
        }
