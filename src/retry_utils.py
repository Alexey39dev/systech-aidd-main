"""Утилиты для retry логики с exponential backoff."""

import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

from .exceptions import RetryError
from .logger import get_logger

T = TypeVar("T")

logger = get_logger("retry_utils")


async def with_exponential_backoff(
    operation: Callable[[], Awaitable[T]],
    *,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 10.0,
    backoff_factor: float = 2.0,
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,),
    operation_name: str = "operation",
) -> T:
    """Выполнить асинхронную операцию с exponential backoff retry.

    Args:
        operation: Асинхронная функция для выполнения
        max_retries: Максимальное количество попыток
        initial_delay: Начальная задержка между попытками (секунды)
        max_delay: Максимальная задержка между попытками (секунды)
        backoff_factor: Множитель для экспоненциального увеличения задержки
        retryable_exceptions: Кортеж исключений, при которых выполняется retry
        operation_name: Имя операции для логирования

    Returns:
        Результат выполнения операции

    Raises:
        Exception: Последнее исключение, если все попытки исчерпаны
    """
    last_exception: Exception | None = None
    retry_delay = initial_delay

    for attempt in range(max_retries):
        try:
            logger.debug(
                "Попытка выполнения операции",
                operation=operation_name,
                attempt=attempt + 1,
                max_retries=max_retries,
            )

            result = await operation()

            if attempt > 0:
                logger.info(
                    "Операция успешно выполнена после повторных попыток",
                    operation=operation_name,
                    attempt=attempt + 1,
                )

            return result

        except retryable_exceptions as e:
            last_exception = e

            # Проверяем, является ли это последней попыткой
            is_last_attempt = attempt >= max_retries - 1

            if is_last_attempt:
                logger.error(
                    "Все попытки выполнения операции исчерпаны",
                    operation=operation_name,
                    max_retries=max_retries,
                    last_error=str(e),
                    error_type=type(e).__name__,
                )
                raise

            # Логируем предупреждение и ждем перед следующей попыткой
            logger.warning(
                "Ошибка при выполнении операции, повторная попытка",
                operation=operation_name,
                error=str(e),
                error_type=type(e).__name__,
                attempt=attempt + 1,
                max_retries=max_retries,
                retry_delay=retry_delay,
            )

            await asyncio.sleep(retry_delay)

            # Экспоненциальный backoff
            retry_delay = min(retry_delay * backoff_factor, max_delay)

    # Этот код не должен быть достижим, но на всякий случай
    if last_exception:
        raise last_exception
    raise RetryError(
        "Не удалось выполнить операцию после всех попыток",
        operation_name=operation_name,
        attempts=max_retries,
    )
