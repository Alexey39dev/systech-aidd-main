"""Тесты для кастомных исключений."""

from src.exceptions import (
    AppError,
    ConfigError,
    LLMClientError,
    LLMConnectionError,
    LLMEmptyResponseError,
    LLMError,
    LLMRateLimitError,
    LLMServerError,
    LLMTimeoutError,
    RetryError,
)


def test_app_error_basic():
    """Тест базового исключения без деталей."""
    error = AppError("Test error")
    assert error.message == "Test error"
    assert error.details == {}
    assert str(error) == "Test error"


def test_app_error_with_details():
    """Тест базового исключения с деталями."""
    error = AppError("Test error", details={"key": "value", "code": "123"})
    assert error.message == "Test error"
    assert error.details == {"key": "value", "code": "123"}
    assert "key=value" in str(error)
    assert "code=123" in str(error)


def test_config_error_inheritance():
    """Тест, что ConfigError наследуется от AppError."""
    error = ConfigError("Config error")
    assert isinstance(error, AppError)
    assert isinstance(error, ConfigError)


def test_llm_error_hierarchy():
    """Тест иерархии LLM исключений."""
    # Базовый LLMError
    base_error = LLMError("LLM error")
    assert isinstance(base_error, AppError)
    assert isinstance(base_error, LLMError)

    # LLMConnectionError
    conn_error = LLMConnectionError("Connection failed")
    assert isinstance(conn_error, AppError)
    assert isinstance(conn_error, LLMError)
    assert isinstance(conn_error, LLMConnectionError)

    # LLMRateLimitError
    rate_error = LLMRateLimitError("Rate limit")
    assert isinstance(rate_error, AppError)
    assert isinstance(rate_error, LLMError)
    assert isinstance(rate_error, LLMRateLimitError)

    # LLMTimeoutError
    timeout_error = LLMTimeoutError("Timeout")
    assert isinstance(timeout_error, AppError)
    assert isinstance(timeout_error, LLMError)
    assert isinstance(timeout_error, LLMTimeoutError)


def test_llm_empty_response_error():
    """Тест LLMEmptyResponseError."""
    error = LLMEmptyResponseError("Empty response")
    assert isinstance(error, LLMError)
    assert error.message == "Empty response"


def test_llm_server_error():
    """Тест LLMServerError."""
    error = LLMServerError("Server error", details={"status_code": "500"})
    assert isinstance(error, LLMError)
    assert error.details["status_code"] == "500"


def test_llm_client_error():
    """Тест LLMClientError."""
    error = LLMClientError("Client error", details={"status_code": "400"})
    assert isinstance(error, LLMError)
    assert error.details["status_code"] == "400"


def test_retry_error():
    """Тест RetryError с расширенными атрибутами."""
    original_error = ValueError("Original error")
    error = RetryError(
        "Retry failed",
        operation_name="test_operation",
        attempts=3,
        last_exception=original_error,
    )

    assert isinstance(error, AppError)
    assert error.message == "Retry failed"
    assert error.operation_name == "test_operation"
    assert error.attempts == 3
    assert error.last_exception is original_error
    assert "operation=test_operation" in str(error)
    assert "attempts=3" in str(error)


def test_exception_chaining():
    """Тест цепочки исключений (raise ... from ...)."""
    original = ValueError("Original")

    try:
        try:
            raise original
        except ValueError as e:
            raise LLMError("Wrapped error") from e
    except LLMError as llm_error:
        assert llm_error.__cause__ is original
        assert isinstance(llm_error.__cause__, ValueError)


def test_catching_by_base_class():
    """Тест перехвата исключений по базовому классу."""
    # Можем ловить все LLM ошибки через LLMError
    errors = [
        LLMConnectionError("conn"),
        LLMRateLimitError("rate"),
        LLMTimeoutError("timeout"),
    ]

    caught_count = 0
    for error in errors:
        try:
            raise error
        except LLMError:
            caught_count += 1

    assert caught_count == 3


def test_catching_by_app_error():
    """Тест перехвата всех кастомных исключений через AppError."""
    errors = [
        ConfigError("config"),
        LLMError("llm"),
        LLMConnectionError("conn"),
        RetryError("retry", "op", 3),
    ]

    caught_count = 0
    for error in errors:
        try:
            raise error
        except AppError:
            caught_count += 1

    assert caught_count == 4
