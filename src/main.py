"""Главный файл для запуска Telegram-бота."""

import asyncio
import signal
import sys

from .config import Config
from .logger import setup_logging, get_logger, log_config_info
from .bot import TelegramBot


async def main():
    """Главная функция запуска бота."""
    logger = get_logger("main")
    
    try:
        # Загрузка конфигурации
        logger.info("Загрузка конфигурации")
        config = Config()
        
        # Настройка логирования
        setup_logging(config.log_level)
        logger.info("Логирование настроено", level=config.log_level)
        
        # Логирование информации о конфигурации
        log_config_info(config)
        
        # Создание и запуск бота
        logger.info("Создание экземпляра бота")
        bot = TelegramBot(config)
        
        # Обработка сигналов для graceful shutdown
        def signal_handler():
            logger.info("Получен сигнал остановки")
            asyncio.create_task(bot.stop())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        logger.info("Запуск бота")
        await bot.start_polling()
        
    except Exception as e:
        logger.error("Критическая ошибка", error=str(e))
        return 1
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nБот остановлен пользователем")
        sys.exit(0)
