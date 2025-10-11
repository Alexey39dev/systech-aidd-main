"""Кастомные исключения приложения."""


class AppError(Exception):
    """Базовое исключение приложения.

    Все кастомные исключения должны наследоваться от этого класса.
    """

    def __init__(self, message: str, details: dict[str, str] | None = None) -> None:
        """Инициализация исключения.

        Args:
            message: Сообщение об ошибке
            details: Дополнительные детали ошибки
        """
        self.message = message
        self.details = details or {}
        super().__init__(message)

    def __str__(self) -> str:
        """Строковое представление ошибки."""
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class ConfigError(AppError):
    """Ошибка конфигурации приложения."""


class LLMError(AppError):
    """Базовое исключение для ошибок работы с LLM."""


class LLMConnectionError(LLMError):
    """Ошибка подключения к LLM API."""


class LLMRateLimitError(LLMError):
    """Превышен rate limit для LLM API."""


class LLMTimeoutError(LLMError):
    """Таймаут при обращении к LLM API."""


class LLMEmptyResponseError(LLMError):
    """LLM вернул пустой ответ."""


class LLMServerError(LLMError):
    """Серверная ошибка LLM API (5xx)."""


class LLMClientError(LLMError):
    """Клиентская ошибка LLM API (4xx)."""


class RetryError(AppError):
    """Ошибка retry механизма - все попытки исчерпаны."""

    def __init__(
        self,
        message: str,
        operation_name: str,
        attempts: int,
        last_exception: Exception | None = None,
    ) -> None:
        """Инициализация ошибки retry.

        Args:
            message: Сообщение об ошибке
            operation_name: Название операции
            attempts: Количество попыток
            last_exception: Последнее исключение
        """
        super().__init__(message, {"operation": operation_name, "attempts": str(attempts)})
        self.operation_name = operation_name
        self.attempts = attempts
        self.last_exception = last_exception
