"""Тесты для LLM клиента."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from openai import APIConnectionError, APIError, APITimeoutError, RateLimitError

from src.config import Config
from src.exceptions import (
    LLMClientError,
    LLMConnectionError,
    LLMEmptyResponseError,
    LLMRateLimitError,
    LLMServerError,
)
from src.llm_client import LLMClient


@pytest.fixture
def config():
    """Фикстура для конфигурации."""
    return Config(openrouter_api_key="test_api_key")


@pytest.fixture
def llm_client(config):
    """Фикстура для LLM клиента."""
    return LLMClient(config)


def test_llm_client_initialization(llm_client):
    """Тест инициализации LLM клиента."""
    assert llm_client.config is not None
    assert llm_client.logger is not None


def test_get_fallback_response(llm_client):
    """Тест fallback ответа."""
    import asyncio

    response = asyncio.run(llm_client.get_fallback_response("Тестовое сообщение"))

    assert isinstance(response, str)
    assert len(response) > 0
    assert "извините" in response.lower() or "ошибка" in response.lower()


def test_get_response_mock(llm_client):
    """Тест получения ответа с моком."""
    # Простой тест без мока - проверяем, что метод существует
    assert hasattr(llm_client, "get_response")
    assert callable(llm_client.get_response)

    # Проверяем, что fallback работает
    import asyncio

    response = asyncio.run(llm_client.get_fallback_response("Тест"))
    assert isinstance(response, str)


@pytest.mark.asyncio
async def test_retry_on_rate_limit(llm_client):
    """Тест retry при rate limit ошибке."""
    llm_client.INITIAL_RETRY_DELAY = 0.01

    mock_choice = Mock()
    mock_choice.message.content = "Success after retry"
    mock_response = Mock()
    mock_response.choices = [mock_choice]
    mock_response.usage = None

    # Создаем правильный RateLimitError
    mock_error_response = Mock()
    mock_error_response.status_code = 429
    error = RateLimitError("Rate limit", response=mock_error_response, body=None)

    with patch.object(
        llm_client.client.chat.completions,
        "create",
        new_callable=AsyncMock,
        side_effect=[error, mock_response],
    ):
        response = await llm_client.get_response("Test")
        assert response == "Success after retry"


@pytest.mark.asyncio
async def test_retry_on_connection_error(llm_client):
    """Тест retry при ошибке подключения."""
    llm_client.INITIAL_RETRY_DELAY = 0.01

    mock_choice = Mock()
    mock_choice.message.content = "Connected"
    mock_response = Mock()
    mock_response.choices = [mock_choice]
    mock_response.usage = None

    # Создаем правильный APIConnectionError
    error = APIConnectionError(request=Mock())

    with patch.object(
        llm_client.client.chat.completions,
        "create",
        new_callable=AsyncMock,
        side_effect=[error, mock_response],
    ):
        response = await llm_client.get_response("Test")
        assert response == "Connected"


@pytest.mark.asyncio
async def test_all_retries_exhausted(llm_client):
    """Тест исчерпания всех попыток."""
    llm_client.INITIAL_RETRY_DELAY = 0.01
    llm_client.MAX_RETRIES = 2

    # Создаем правильный RateLimitError
    mock_error_response = Mock()
    mock_error_response.status_code = 429
    error = RateLimitError("Rate limit", response=mock_error_response, body=None)

    with (
        patch.object(
            llm_client.client.chat.completions, "create", new_callable=AsyncMock, side_effect=error
        ),
        pytest.raises(LLMRateLimitError),
    ):
        await llm_client.get_response("Test")


# === Новые тесты для непокрытых участков ===


@pytest.mark.asyncio
async def test_get_response_empty_response(llm_client):
    """Тест обработки пустого ответа от LLM."""
    mock_choice = Mock()
    mock_choice.message.content = None  # Пустой ответ
    mock_response = Mock()
    mock_response.choices = [mock_choice]
    mock_response.usage = None

    with (
        patch.object(
            llm_client.client.chat.completions,
            "create",
            new_callable=AsyncMock,
            return_value=mock_response,
        ),
        pytest.raises(LLMEmptyResponseError),
    ):
        await llm_client.get_response("Test")


@pytest.mark.asyncio
async def test_get_response_timeout(llm_client):
    """Тест обработки таймаута."""
    llm_client.INITIAL_RETRY_DELAY = 0.01
    llm_client.MAX_RETRIES = 2

    error = APITimeoutError(request=Mock())

    # APITimeoutError наследуется от APIConnectionError, поэтому
    # перехватывается блоком APIConnectionError
    with (
        patch.object(
            llm_client.client.chat.completions, "create", new_callable=AsyncMock, side_effect=error
        ),
        pytest.raises(LLMConnectionError),
    ):
        await llm_client.get_response("Test")


@pytest.mark.asyncio
async def test_get_response_server_error_5xx(llm_client):
    """Тест обработки серверных ошибок (5xx)."""
    llm_client.INITIAL_RETRY_DELAY = 0.01
    llm_client.MAX_RETRIES = 2

    # Создаем APIError с status_code=500
    error = APIError(
        message="Internal Server Error",
        request=Mock(),
        body=None,
    )
    error.status_code = 500

    with (
        patch.object(
            llm_client.client.chat.completions, "create", new_callable=AsyncMock, side_effect=error
        ),
        pytest.raises(LLMServerError),
    ):
        await llm_client.get_response("Test")


@pytest.mark.asyncio
async def test_get_response_client_error_4xx(llm_client):
    """Тест обработки клиентских ошибок (4xx)."""
    # Создаем APIError с status_code=400
    error = APIError(
        message="Bad Request",
        request=Mock(),
        body=None,
    )
    error.status_code = 400

    with (
        patch.object(
            llm_client.client.chat.completions, "create", new_callable=AsyncMock, side_effect=error
        ),
        pytest.raises(LLMClientError),
    ):
        await llm_client.get_response("Test")


@pytest.mark.asyncio
async def test_connection_success(llm_client):
    """Тест успешного подключения к LLM."""
    mock_choice = Mock()
    mock_choice.message.content = "Test response"
    mock_response = Mock()
    mock_response.choices = [mock_choice]
    mock_response.usage = None

    with patch.object(
        llm_client.client.chat.completions,
        "create",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        result = await llm_client.test_connection()
        assert result is True


@pytest.mark.asyncio
async def test_connection_failure(llm_client):
    """Тест неудачного подключения к LLM."""
    error = APIConnectionError(request=Mock())

    with patch.object(
        llm_client.client.chat.completions, "create", new_callable=AsyncMock, side_effect=error
    ):
        result = await llm_client.test_connection()
        assert result is False
