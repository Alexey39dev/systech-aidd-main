"""Клиент для работы с LLM через OpenRouter."""

from openai import APIConnectionError, APIError, APITimeoutError, AsyncOpenAI, RateLimitError

from .config import Config
from .exceptions import (
    LLMClientError,
    LLMConnectionError,
    LLMEmptyResponseError,
    LLMRateLimitError,
    LLMServerError,
    LLMTimeoutError,
)
from .logger import get_logger
from .messages import FallbackMessages
from .retry_utils import with_exponential_backoff
from .types import Message


class LLMClient:
    """Клиент для работы с LLM через OpenRouter."""

    # Параметры retry логики
    MAX_RETRIES = 3
    INITIAL_RETRY_DELAY = 1.0  # секунды
    MAX_RETRY_DELAY = 10.0  # секунды

    def __init__(self, config: Config):
        """Инициализация LLM клиента.

        Args:
            config: Конфигурация приложения
        """
        self.config = config
        self.logger = get_logger("llm_client")

        # Настройка OpenAI клиента для OpenRouter
        self.client = AsyncOpenAI(
            api_key=config.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            timeout=30.0,  # Таймаут запроса
            max_retries=0,  # Отключаем встроенные retry, чтобы контролировать их самостоятельно
        )

        self.logger.info(
            "LLM клиент инициализирован",
            model=config.llm_model,
            base_url="https://openrouter.ai/api/v1",
            max_retries=self.MAX_RETRIES,
        )

    async def get_response(
        self,
        user_message: str,
        system_prompt: str | None = None,
        conversation_history: list[Message] | None = None,
    ) -> str:
        """Получить ответ от LLM с retry логикой.

        Args:
            user_message: Сообщение пользователя
            system_prompt: Системный промпт (по умолчанию из конфигурации)
            conversation_history: История диалога (типизированные сообщения)

        Returns:
            Ответ от LLM

        Raises:
            Exception: При ошибке обращения к LLM после всех попыток
        """
        # Подготовка сообщений
        messages: list[Message] = []

        # Системный промпт
        if system_prompt is None:
            system_prompt = self.config.system_prompt
        messages.append({"role": "system", "content": system_prompt})

        # История диалога
        if conversation_history:
            messages.extend(conversation_history)

        # Текущее сообщение пользователя
        messages.append({"role": "user", "content": user_message})

        # Определяем исключения, при которых выполняем retry
        retryable_exceptions = (
            LLMRateLimitError,
            LLMConnectionError,
            LLMTimeoutError,
            LLMServerError,
        )

        async def _make_llm_request() -> str:
            """Внутренняя функция для выполнения запроса к LLM."""
            try:
                self.logger.info(
                    "Отправка запроса к LLM",
                    model=self.config.llm_model,
                    messages_count=len(messages),
                    user_message_length=len(user_message),
                )

                # Запрос к LLM
                response = await self.client.chat.completions.create(
                    model=self.config.llm_model,
                    messages=messages,  # type: ignore[arg-type]
                    temperature=self.config.llm_temperature,
                    max_tokens=self.config.llm_max_tokens,
                )

                # Извлечение ответа
                llm_response = response.choices[0].message.content
                if llm_response is None:
                    raise LLMEmptyResponseError("LLM вернул пустой ответ")

                self.logger.info(
                    "Получен ответ от LLM",
                    response_length=len(llm_response),
                    tokens_used=response.usage.total_tokens if response.usage else None,
                    model=self.config.llm_model,
                )

                return llm_response

            except RateLimitError as e:
                # Оборачиваем в кастомное исключение
                raise LLMRateLimitError(
                    "Превышен rate limit LLM API", details={"original_error": str(e)}
                ) from e

            except APIConnectionError as e:
                raise LLMConnectionError(
                    "Ошибка подключения к LLM API", details={"original_error": str(e)}
                ) from e

            except APITimeoutError as e:
                raise LLMTimeoutError(
                    "Таймаут при обращении к LLM API", details={"original_error": str(e)}
                ) from e

            except APIError as e:
                # Для серверных ошибок (5xx) делаем retry
                if hasattr(e, "status_code") and 500 <= e.status_code < 600:
                    self.logger.warning(
                        "Серверная ошибка API",
                        error=str(e),
                        status_code=e.status_code,
                    )
                    raise LLMServerError(
                        "Серверная ошибка LLM API",
                        details={"status_code": str(e.status_code), "error": str(e)},
                    ) from e
                else:
                    # Для клиентских ошибок (4xx) не делаем retry
                    self.logger.error(
                        "Клиентская ошибка API, retry не выполняется",
                        error=str(e),
                        status_code=getattr(e, "status_code", None),
                    )
                    raise LLMClientError(
                        "Клиентская ошибка LLM API",
                        details={
                            "status_code": str(getattr(e, "status_code", "unknown")),
                            "error": str(e),
                        },
                    ) from e

        # Выполняем запрос с retry логикой
        return await with_exponential_backoff(
            _make_llm_request,
            max_retries=self.MAX_RETRIES,
            initial_delay=self.INITIAL_RETRY_DELAY,
            max_delay=self.MAX_RETRY_DELAY,
            backoff_factor=2.0,
            retryable_exceptions=retryable_exceptions,
            operation_name="LLM API request",
        )

    async def get_fallback_response(self, user_message: str) -> str:
        """Получить fallback ответ при ошибке LLM.

        Args:
            user_message: Сообщение пользователя

        Returns:
            Fallback ответ
        """
        self.logger.warning("Использование fallback ответа", user_message_length=len(user_message))

        fallback_responses = FallbackMessages.get_all()

        # Простой fallback на основе длины сообщения
        response_index = len(user_message) % len(fallback_responses)
        selected_response = fallback_responses[response_index]

        self.logger.info("Выбран fallback ответ", response_index=response_index)
        return selected_response

    async def test_connection(self) -> bool:
        """Тестирование подключения к LLM.

        Returns:
            True если подключение работает, False иначе
        """
        try:
            test_response = await self.get_response("Привет! Это тестовое сообщение.")
            self.logger.info("Тест подключения к LLM успешен", response_length=len(test_response))
            return True
        except Exception as e:
            self.logger.error("Тест подключения к LLM не удался", error=str(e))
            return False
