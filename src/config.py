"""Конфигурация приложения."""

from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Конфигурация приложения с валидацией через Pydantic."""

    # OpenRouter API Configuration
    openrouter_api_key: str = Field(..., description="OpenRouter API Key")

    # LLM Configuration
    system_prompt: str = Field(
        default="Ты полезный ассистент. Отвечай на вопросы пользователя дружелюбно и информативно.",
        description="System prompt for LLM",
    )
    max_history: int = Field(default=10, ge=1, le=50, description="Maximum dialog history length")
    llm_model: str = Field(default="openai/gpt-3.5-turbo", description="LLM model name")
    llm_temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="LLM temperature")
    llm_max_tokens: int = Field(
        default=1000, ge=100, le=4000, description="Maximum tokens for LLM response"
    )

    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_to_file: bool = Field(default=False, description="Enable logging to file")
    log_file_path: str = Field(default="logs/app.log", description="Path to log file")
    log_colorful: bool = Field(default=True, description="Enable colorful console output for logs")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "env_prefix": "",
        "extra": "ignore",
    }

    def __str__(self) -> str:
        """Строковое представление конфигурации (без секретных данных)."""
        return (
            f"Config("
            f"system_prompt='{self.system_prompt[:50]}...', "
            f"max_history={self.max_history}, "
            f"llm_model='{self.llm_model}', "
            f"llm_temperature={self.llm_temperature}, "
            f"llm_max_tokens={self.llm_max_tokens}, "
            f"log_level='{self.log_level}', "
            f"log_to_file={self.log_to_file}"
            f")"
        )
