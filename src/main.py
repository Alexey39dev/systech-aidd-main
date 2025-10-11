"""Главный файл для запуска консольного LLM-ассистента."""

import asyncio
import signal
import sys
from pydantic import ValidationError

from .config import Config
from .logger import setup_logging, get_logger
from .console import ConsoleApp


# Глобальная переменная для приложения (для обработки сигналов)
_app_instance = None


def handle_shutdown_signal(signum, frame):
    """Обработка сигналов завершения."""
    global _app_instance
    if _app_instance and _app_instance.is_running:
        print("\n\nПолучен сигнал завершения. Завершаю работу...")
        asyncio.create_task(_app_instance.stop())


async def main():
    """Главная функция запуска приложения с улучшенной обработкой ошибок."""
    global _app_instance
    
    # Базовая настройка логирования для начала
    setup_logging("INFO", console_output=False)
    logger = get_logger("main")
    
    try:
        # Загрузка конфигурации с обработкой ошибок валидации
        try:
            config = Config()
        except ValidationError as e:
            logger.error("Ошибка валидации конфигурации", error=str(e))
            print("\nОшибка конфигурации:")
            print(f"  {str(e)}")
            print("\nПроверьте файл .env и убедитесь, что все обязательные параметры заданы.")
            return 1
        except FileNotFoundError:
            logger.error("Файл .env не найден")
            print("\nОшибка: файл .env не найден.")
            print("Создайте файл .env на основе .env.example")
            return 1
        except Exception as e:
            logger.error("Ошибка загрузки конфигурации", error=str(e), error_type=type(e).__name__)
            print(f"\nНе удалось загрузить конфигурацию: {str(e)}")
            return 1
        
        # Обновление настроек логирования на основе конфигурации
        setup_logging(config.log_level, console_output=False)
        logger.info("Конфигурация успешно загружена")
        
        # Создание консольного приложения
        try:
            app = ConsoleApp(config)
            _app_instance = app
        except Exception as e:
            logger.error("Ошибка создания приложения", error=str(e), error_type=type(e).__name__)
            print(f"\nНе удалось создать приложение: {str(e)}")
            return 1
        
        # Настройка обработки сигналов для graceful shutdown
        signal.signal(signal.SIGINT, handle_shutdown_signal)
        signal.signal(signal.SIGTERM, handle_shutdown_signal)
        
        # Запуск приложения
        logger.info("Запуск консольного приложения")
        await app.run()
        logger.info("Приложение завершило работу")
        
    except KeyboardInterrupt:
        logger.info("Приложение прервано пользователем (Ctrl+C)")
        print("\n\nПриложение остановлено пользователем")
        return 0
        
    except Exception as e:
        logger.error("Критическая ошибка", error=str(e), error_type=type(e).__name__)
        print(f"\nКритическая ошибка: {str(e)}")
        return 1
    
    finally:
        logger.info("Очистка ресурсов")
        _app_instance = None
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nПриложение остановлено пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\nФатальная ошибка: {str(e)}")
        sys.exit(1)
