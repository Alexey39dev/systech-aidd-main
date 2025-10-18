"""Конфигурация приложения."""

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Конфигурация приложения с валидацией через Pydantic."""

    # OpenRouter API Configuration
    openrouter_api_key: str = Field(default="test_key", description="OpenRouter API Key")

    # LLM Configuration
    system_prompt: str = Field(
        default="Ты полезный ассистент. Отвечай на вопросы пользователя дружелюбно и информативно.",
        description="System prompt for LLM",
    )
    system_prompt_file: str | None = Field(
        default=None, description="Path to system prompt file (overrides system_prompt)"
    )
    max_history: int = Field(default=10, ge=1, le=50, description="Maximum dialog history length")
    llm_model: str = Field(default="openai/gpt-3.5-turbo", description="LLM model name")
    llm_temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="LLM temperature")
    llm_max_tokens: int = Field(
        default=1000, ge=100, le=4000, description="Maximum tokens for LLM response"
    )

    # Database Configuration
    database_url: str = Field(
        default="postgresql://aidd_user:aidd_password@localhost:5434/aidd_db",
        description="PostgreSQL database connection URL",
    )
    database_pool_min_size: int = Field(
        default=5, ge=1, le=50, description="Minimum database connection pool size"
    )
    database_pool_max_size: int = Field(
        default=20, ge=1, le=100, description="Maximum database connection pool size"
    )

    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_to_file: bool = Field(default=False, description="Enable logging to file")
    log_file_path: str = Field(default="logs/app.log", description="Path to log file")
    log_colorful: bool = Field(default=True, description="Enable colorful console output for logs")

    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API server host")
    api_port: int = Field(default=8000, ge=1, le=65535, description="API server port")
    api_reload: bool = Field(default=True, description="Enable auto-reload in development mode")
    stat_collector_type: str = Field(
        default="mock",
        description="Type of stat collector to use: 'mock' or 'real'",
    )

    # Chat Configuration
    chat_enabled: bool = Field(default=True, description="Enable chat API")
    text_to_sql_enabled: bool = Field(default=True, description="Enable admin mode with text-to-SQL")
    session_expire_hours: int = Field(
        default=24, ge=1, le=168, description="Session expiration time in hours"
    )

    # Bot Configuration
    bot_username: str = Field(default="docker-user", description="Bot username for Docker container")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "env_prefix": "",
        "extra": "ignore",
    }

    @field_validator("system_prompt_file")
    @classmethod
    def validate_prompt_file(cls, v: str | None) -> str | None:
        """Валидация пути к файлу промпта.

        Args:
            v: Путь к файлу (опционально)

        Returns:
            Валидный путь или None

        Raises:
            ValueError: Если файл указан, но не существует
        """
        if v is not None and not Path(v).exists():
            raise ValueError(f"Prompt file not found: {v}")
        return v

    def __str__(self) -> str:
        """Строковое представление конфигурации (без секретных данных)."""
        # Скрываем пароль в database_url
        db_url_masked = self.database_url.split("@")[-1] if "@" in self.database_url else "***"
        return (
            f"Config("
            f"system_prompt='{self.system_prompt[:50]}...', "
            f"max_history={self.max_history}, "
            f"llm_model='{self.llm_model}', "
            f"llm_temperature={self.llm_temperature}, "
            f"llm_max_tokens={self.llm_max_tokens}, "
            f"database='{db_url_masked}', "
            f"db_pool={self.database_pool_min_size}-{self.database_pool_max_size}, "
            f"log_level='{self.log_level}', "
            f"log_to_file={self.log_to_file}, "
            f"api={self.api_host}:{self.api_port}, "
            f"stat_collector={self.stat_collector_type}"
            f")"
        )
