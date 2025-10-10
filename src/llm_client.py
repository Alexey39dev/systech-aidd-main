"""Клиент для работы с LLM через OpenRouter."""

import asyncio
from openai import AsyncOpenAI
from typing import Optional, List, Dict, Any

from .config import Config
from .logger import get_logger


class LLMClient:
    """Клиент для работы с LLM через OpenRouter."""
    
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
            base_url="https://openrouter.ai/api/v1"
        )
        
        self.logger.info(
            "LLM клиент инициализирован",
            model=config.llm_model,
            base_url="https://openrouter.ai/api/v1"
        )
    
    async def get_response(
        self, 
        user_message: str, 
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Получить ответ от LLM.
        
        Args:
            user_message: Сообщение пользователя
            system_prompt: Системный промпт (по умолчанию из конфигурации)
            conversation_history: История диалога
            
        Returns:
            Ответ от LLM
            
        Raises:
            Exception: При ошибке обращения к LLM
        """
        try:
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
            
            self.logger.info(
                "Отправка запроса к LLM",
                model=self.config.llm_model,
                messages_count=len(messages),
                user_message_length=len(user_message)
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
                model=self.config.llm_model
            )
            
            return llm_response
            
        except Exception as e:
            self.logger.error("Ошибка обращения к LLM", error=str(e), model=self.config.llm_model)
            raise
    
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
