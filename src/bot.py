"""Telegram бот для обработки сообщений."""

import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.exceptions import TelegramAPIError

from .config import Config
from .logger import setup_logging, get_logger
from .llm_client import LLMClient


class TelegramBot:
    """Telegram бот для обработки сообщений."""
    
    def __init__(self, config: Config):
        """Инициализация бота.
        
        Args:
            config: Конфигурация приложения
        """
        self.config = config
        self.bot = Bot(token=config.telegram_bot_token)
        self.dp = Dispatcher()
        self.logger = get_logger("telegram_bot")
        
        # Инициализация LLM клиента
        self.llm_client = LLMClient(config)
        
        # Регистрация обработчиков
        self._register_handlers()
    
    def _register_handlers(self):
        """Регистрация обработчиков команд и сообщений."""
        self.dp.message.register(self.start_command, Command("start"))
        self.dp.message.register(self.echo_message)
    
    async def start_command(self, message: Message):
        """Обработка команды /start.
        
        Args:
            message: Сообщение от пользователя
        """
        user_id = message.from_user.id
        self.logger.info("Получена команда /start", user_id=user_id)
        
        welcome_text = (
            "Привет! Я LLM-ассистент.\n"
            "Отправь мне любое сообщение, и я отвечу на него.\n"
            "Используй /start для повторного приветствия."
        )
        
        try:
            await message.answer(welcome_text)
            self.logger.info("Отправлен ответ на /start", user_id=user_id)
        except TelegramAPIError as e:
            self.logger.error("Ошибка отправки ответа на /start", user_id=user_id, error=str(e))
    
    async def echo_message(self, message: Message):
        """Обработка сообщений через LLM.
        
        Args:
            message: Сообщение от пользователя
        """
        user_id = message.from_user.id
        user_text = message.text or "[не текстовое сообщение]"
        
        self.logger.info("Получено сообщение", user_id=user_id, text=user_text[:100])
        
        try:
            # Получение ответа от LLM
            response = await self.llm_client.get_response(user_text)
            
            await message.answer(response)
            self.logger.info("Отправлен ответ от LLM", user_id=user_id, response_length=len(response))
            
        except Exception as e:
            self.logger.error("Ошибка LLM", user_id=user_id, error=str(e))
            
            try:
                # Fallback ответ
                fallback_response = await self.llm_client.get_fallback_response(user_text)
                await message.answer(fallback_response)
                self.logger.info("Отправлен fallback ответ", user_id=user_id)
            except TelegramAPIError as telegram_error:
                self.logger.error("Ошибка отправки fallback ответа", user_id=user_id, error=str(telegram_error))
    
    async def start_polling(self):
        """Запуск бота в режиме polling."""
        self.logger.info("Запуск бота в режиме polling")
        
        try:
            await self.dp.start_polling(self.bot)
        except Exception as e:
            self.logger.error("Критическая ошибка бота", error=str(e))
            raise
        finally:
            await self.bot.session.close()
    
    async def stop(self):
        """Остановка бота."""
        self.logger.info("Остановка бота")
        await self.bot.session.close()
