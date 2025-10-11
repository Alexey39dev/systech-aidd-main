"""Клиент для работы с LLM через OpenRouter."""

import asyncio
from openai import AsyncOpenAI, APIError, APIConnectionError, RateLimitError, APITimeoutError
from typing import Optional, List, Dict, Any

from .config import Config
from .logger import get_logger


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
            max_retries=0  # Отключаем встроенные retry, чтобы контролировать их самостоятельно
        )
        
        self.logger.info(
            "LLM клиент инициализирован",
            model=config.llm_model,
            base_url="https://openrouter.ai/api/v1",
            max_retries=self.MAX_RETRIES
        )
    
    async def get_response(
        self, 
        user_message: str, 
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Получить ответ от LLM с retry логикой.
        
        Args:
            user_message: Сообщение пользователя
            system_prompt: Системный промпт (по умолчанию из конфигурации)
            conversation_history: История диалога
            
        Returns:
            Ответ от LLM
            
        Raises:
            Exception: При ошибке обращения к LLM после всех попыток
        """
        # Подготовка сообщений
        messages = []
        
        # Системный промпт
        if system_prompt is None:
            system_prompt = self.config.system_prompt
        messages.append({"role": "system", "content": system_prompt})
        
        # История диалога
        if conversation_history:
            messages.extend(conversation_history)
        
        # Текущее сообщение пользователя
        messages.append({"role": "user", "content": user_message})
        
        # Retry логика с экспоненциальным backoff
        last_exception = None
        retry_delay = self.INITIAL_RETRY_DELAY
        
        for attempt in range(self.MAX_RETRIES):
            try:
                self.logger.info(
                    "Отправка запроса к LLM",
                    model=self.config.llm_model,
                    messages_count=len(messages),
                    user_message_length=len(user_message),
                    attempt=attempt + 1,
                    max_retries=self.MAX_RETRIES
                )
                
                # Запрос к LLM
                response = await self.client.chat.completions.create(
                    model=self.config.llm_model,
                    messages=messages,
                    temperature=self.config.llm_temperature,
                    max_tokens=self.config.llm_max_tokens
                )
                
                # Извлечение ответа
                llm_response = response.choices[0].message.content
                
                self.logger.info(
                    "Получен ответ от LLM",
                    response_length=len(llm_response),
                    tokens_used=response.usage.total_tokens if response.usage else None,
                    model=self.config.llm_model,
                    attempt=attempt + 1
                )
                
                return llm_response
            
            except RateLimitError as e:
                last_exception = e
                self.logger.warning(
                    "Rate limit превышен, повторная попытка",
                    error=str(e),
                    attempt=attempt + 1,
                    max_retries=self.MAX_RETRIES,
                    retry_delay=retry_delay
                )
                
            except APIConnectionError as e:
                last_exception = e
                self.logger.warning(
                    "Ошибка подключения к API, повторная попытка",
                    error=str(e),
                    attempt=attempt + 1,
                    max_retries=self.MAX_RETRIES,
                    retry_delay=retry_delay
                )
                
            except APITimeoutError as e:
                last_exception = e
                self.logger.warning(
                    "Таймаут API, повторная попытка",
                    error=str(e),
                    attempt=attempt + 1,
                    max_retries=self.MAX_RETRIES,
                    retry_delay=retry_delay
                )
                
            except APIError as e:
                last_exception = e
                self.logger.error(
                    "Ошибка API",
                    error=str(e),
                    status_code=getattr(e, 'status_code', None),
                    attempt=attempt + 1,
                    max_retries=self.MAX_RETRIES
                )
                # Для серверных ошибок (5xx) делаем retry
                if hasattr(e, 'status_code') and 500 <= e.status_code < 600:
                    self.logger.warning("Серверная ошибка, повторная попытка", retry_delay=retry_delay)
                else:
                    # Для клиентских ошибок (4xx) не делаем retry
                    self.logger.error("Клиентская ошибка, retry не выполняется")
                    raise
                    
            except Exception as e:
                last_exception = e
                self.logger.error(
                    "Неожиданная ошибка обращения к LLM",
                    error=str(e),
                    error_type=type(e).__name__,
                    attempt=attempt + 1,
                    max_retries=self.MAX_RETRIES
                )
                # Для неизвестных ошибок прерываем retry
                raise
            
            # Если не последняя попытка, ждем перед повторной попыткой
            if attempt < self.MAX_RETRIES - 1:
                await asyncio.sleep(retry_delay)
                # Экспоненциальный backoff
                retry_delay = min(retry_delay * 2, self.MAX_RETRY_DELAY)
        
        # Все попытки исчерпаны
        self.logger.error(
            "Все попытки обращения к LLM исчерпаны",
            max_retries=self.MAX_RETRIES,
            last_error=str(last_exception) if last_exception else "Unknown"
        )
        
        if last_exception:
            raise last_exception
        else:
            raise Exception("Не удалось получить ответ от LLM после всех попыток")
    
    async def get_fallback_response(self, user_message: str) -> str:
        """Получить fallback ответ при ошибке LLM.
        
        Args:
            user_message: Сообщение пользователя
            
        Returns:
            Fallback ответ
        """
        self.logger.warning("Использование fallback ответа", user_message_length=len(user_message))
        
        fallback_responses = [
            "Извините, у меня временные технические проблемы. Попробуйте позже.",
            "К сожалению, я не могу ответить сейчас. Обратитесь позже.",
            "Произошла ошибка при обработке вашего запроса. Попробуйте еще раз.",
            "Сейчас у меня проблемы с подключением к сервису. Попробуйте через несколько минут."
        ]
        
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
