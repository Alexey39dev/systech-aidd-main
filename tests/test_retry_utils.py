"""Тесты для модуля retry_utils."""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from src.retry_utils import with_exponential_backoff


class CustomRetryableError(Exception):
    """Кастомное исключение для тестирования retry."""


class NonRetryableError(Exception):
    """Исключение, которое не должно вызывать retry."""


@pytest.mark.asyncio
class TestWithExponentialBackoff:
    """Тесты для функции with_exponential_backoff."""

    async def test_successful_operation_first_attempt(self):
        """Тест успешного выполнения операции с первой попытки."""
        mock_operation = AsyncMock(return_value="success")

        result = await with_exponential_backoff(
            mock_operation,
            max_retries=3,
            initial_delay=0.01,
            operation_name="test_operation",
        )

        assert result == "success"
        assert mock_operation.call_count == 1

    async def test_successful_after_retries(self):
        """Тест успешного выполнения после нескольких попыток."""
        mock_operation = AsyncMock(
            side_effect=[
                CustomRetryableError("First attempt failed"),
                CustomRetryableError("Second attempt failed"),
                "success",
            ]
        )

        result = await with_exponential_backoff(
            mock_operation,
            max_retries=3,
            initial_delay=0.01,
            max_delay=0.05,
            retryable_exceptions=(CustomRetryableError,),
            operation_name="test_operation",
        )

        assert result == "success"
        assert mock_operation.call_count == 3

    async def test_all_retries_exhausted(self):
        """Тест исчерпания всех попыток."""
        mock_operation = AsyncMock(side_effect=CustomRetryableError("Always fails"))

        with pytest.raises(CustomRetryableError, match="Always fails"):
            await with_exponential_backoff(
                mock_operation,
                max_retries=3,
                initial_delay=0.01,
                retryable_exceptions=(CustomRetryableError,),
                operation_name="test_operation",
            )

        assert mock_operation.call_count == 3

    async def test_non_retryable_exception(self):
        """Тест, что не-ретряемое исключение не вызывает повторов."""
        mock_operation = AsyncMock(side_effect=NonRetryableError("Non-retryable error"))

        with pytest.raises(NonRetryableError, match="Non-retryable error"):
            await with_exponential_backoff(
                mock_operation,
                max_retries=3,
                initial_delay=0.01,
                retryable_exceptions=(CustomRetryableError,),
                operation_name="test_operation",
            )

        # Операция должна быть вызвана только один раз, без retry
        assert mock_operation.call_count == 1

    async def test_exponential_backoff_timing(self):
        """Тест экспоненциального увеличения задержки."""
        mock_operation = AsyncMock(
            side_effect=[
                CustomRetryableError("Attempt 1"),
                CustomRetryableError("Attempt 2"),
                "success",
            ]
        )

        start_time = asyncio.get_event_loop().time()

        await with_exponential_backoff(
            mock_operation,
            max_retries=3,
            initial_delay=0.05,
            max_delay=0.2,
            backoff_factor=2.0,
            retryable_exceptions=(CustomRetryableError,),
            operation_name="test_operation",
        )

        elapsed_time = asyncio.get_event_loop().time() - start_time

        # Ожидаемое время: 0.05 (первая задержка) + 0.1 (вторая задержка) = 0.15
        # Добавляем небольшой запас на выполнение кода
        assert elapsed_time >= 0.15
        assert elapsed_time < 0.3  # Не должно быть слишком долго

    async def test_max_delay_limit(self):
        """Тест, что задержка не превышает max_delay."""
        call_delays = []

        async def operation_with_timing():
            if len(call_delays) > 0:
                # Записываем время с момента предыдущего вызова
                call_delays.append(asyncio.get_event_loop().time())
            else:
                call_delays.append(asyncio.get_event_loop().time())

            if len(call_delays) < 5:
                raise CustomRetryableError(f"Attempt {len(call_delays)}")
            return "success"

        await with_exponential_backoff(
            operation_with_timing,
            max_retries=5,
            initial_delay=0.01,
            max_delay=0.05,  # Максимальная задержка
            backoff_factor=10.0,  # Большой множитель, чтобы быстро достичь max_delay
            retryable_exceptions=(CustomRetryableError,),
            operation_name="test_operation",
        )

        # Проверяем, что было 5 вызовов
        assert len(call_delays) == 5

        # Вычисляем реальные задержки между вызовами
        actual_delays = [call_delays[i] - call_delays[i - 1] for i in range(1, len(call_delays))]

        # Все задержки должны быть <= max_delay (с небольшим запасом на точность)
        for delay in actual_delays:
            assert delay <= 0.08, f"Delay {delay} exceeds max_delay tolerance"

    async def test_default_parameters(self):
        """Тест работы с параметрами по умолчанию."""
        mock_operation = AsyncMock(return_value="success")

        result = await with_exponential_backoff(mock_operation)

        assert result == "success"
        assert mock_operation.call_count == 1

    async def test_multiple_retryable_exceptions(self):
        """Тест с несколькими типами ретряемых исключений."""
        mock_operation = AsyncMock(
            side_effect=[
                CustomRetryableError("First error"),
                NonRetryableError("Second error (but retryable in this test)"),
                "success",
            ]
        )

        result = await with_exponential_backoff(
            mock_operation,
            max_retries=3,
            initial_delay=0.01,
            retryable_exceptions=(CustomRetryableError, NonRetryableError),
            operation_name="test_operation",
        )

        assert result == "success"
        assert mock_operation.call_count == 3

    async def test_logging(self):
        """Тест, что retry логирует события."""
        mock_operation = AsyncMock(
            side_effect=[
                CustomRetryableError("Attempt 1"),
                "success",
            ]
        )

        with patch("src.retry_utils.logger") as mock_logger:
            result = await with_exponential_backoff(
                mock_operation,
                max_retries=3,
                initial_delay=0.01,
                retryable_exceptions=(CustomRetryableError,),
                operation_name="test_operation",
            )

            assert result == "success"

            # Проверяем, что были вызовы логирования
            assert mock_logger.debug.call_count >= 1  # Попытки выполнения
            assert mock_logger.warning.call_count >= 1  # Ошибка и retry
            assert mock_logger.info.call_count >= 1  # Успех после retry

    async def test_operation_returns_none(self):
        """Тест, что функция корректно обрабатывает операции, возвращающие None."""
        mock_operation = AsyncMock(return_value=None)

        result = await with_exponential_backoff(
            mock_operation,
            max_retries=3,
            operation_name="test_operation",
        )

        assert result is None
        assert mock_operation.call_count == 1

    async def test_zero_retries(self):
        """Тест с нулевым количеством retry (не должно быть повторов)."""
        mock_operation = AsyncMock(side_effect=CustomRetryableError("Always fails"))

        with pytest.raises(CustomRetryableError):
            await with_exponential_backoff(
                mock_operation,
                max_retries=1,  # Только одна попытка, без retry
                initial_delay=0.01,
                retryable_exceptions=(CustomRetryableError,),
                operation_name="test_operation",
            )

        assert mock_operation.call_count == 1
