"""Главный файл для запуска консольного LLM-ассистента."""

import asyncio
import signal
import sys
from collections.abc import Callable
from typing import Any

from pydantic import ValidationError

from .config import Config
from .console import ConsoleApp
from .exceptions import ConfigError
from .logger import get_logger, setup_logging
from .messages import ErrorMessages, InfoMessages


class ApplicationContext:
    """Контекст приложения для управления жизненным циклом."""

    def __init__(self) -> None:
        """Инициализация контекста приложения."""
        self.app: ConsoleApp | None = None
        self.logger = get_logger("context")
        self._shutdown_event = asyncio.Event()

    def set_app(self, app: ConsoleApp) -> None:
        """Установить экземпляр приложения.

        Args:
            app: Экземпляр консольного приложения
        """
        self.app = app
        self.logger.info("Приложение установлено в контекст")

    def request_shutdown(self) -> None:
        """Запросить остановку приложения.

        Вызывается из обработчика сигналов.
        Устанавливает флаг для корректного завершения.
        """
        if self.app and self.app.is_running:
            self.logger.info("Получен запрос на остановку приложения")
            self._shutdown_event.set()

    async def shutdown(self) -> None:
        """Остановить приложение асинхронно."""
        if self.app and self.app.is_running:
            self.logger.info("Остановка приложения...")
            await self.app.stop()
            self.logger.info("Приложение остановлено")

    async def wait_for_shutdown(self) -> None:
        """Ожидать сигнала остановки."""
        await self._shutdown_event.wait()

    def cleanup(self) -> None:
        """Очистить ресурсы контекста."""
        self.app = None
        self.logger.info("Контекст приложения очищен")


def create_shutdown_handler(
    context: ApplicationContext,
) -> Callable[[int, Any], None]:
    """Создать обработчик сигналов завершения.

    Args:
        context: Контекст приложения

    Returns:
        Функция-обработчик сигналов
    """

    def handler(signum: int, frame: Any) -> None:
        """Обработать сигнал завершения."""
        print(InfoMessages.SHUTDOWN_SIGNAL.value)
        context.request_shutdown()

    return handler


async def main() -> int:
    """Главная функция запуска приложения с улучшенной обработкой ошибок.

    Returns:
        Код возврата: 0 - успех, 1 - ошибка
    """
    # Создание контекста приложения
    context = ApplicationContext()

    # Базовая настройка логирования для начала (без цветов и файла)
    setup_logging("INFO", console_output=False, colorful=False)
    logger = get_logger("main")

    try:
        # Загрузка конфигурации с обработкой ошибок валидации
        try:
            config = Config()  # type: ignore[call-arg]
        except ValidationError as e:
            # Оборачиваем в кастомное исключение
            raise ConfigError(
                "Ошибка валидации конфигурации", details={"validation_error": str(e)}
            ) from e

        except ConfigError as e:
            logger.error("Ошибка конфигурации", error=str(e), details=e.details)
            print(ErrorMessages.CONFIG_ERROR.value)
            print(f"  {str(e)}")
            print(ErrorMessages.CONFIG_CHECK_PARAMS.value)
            return 1
        except FileNotFoundError:
            logger.error("Файл .env не найден")
            print(ErrorMessages.ENV_NOT_FOUND.value)
            print(ErrorMessages.ENV_INSTRUCTION.value)
            return 1
        except Exception as e:
            logger.error(
                "Ошибка загрузки конфигурации",
                error=str(e),
                error_type=type(e).__name__,
            )
            print(ErrorMessages.CRITICAL_ERROR.value.format(error=str(e)))
            return 1

        # Обновление настроек логирования на основе конфигурации
        setup_logging(
            log_level=config.log_level,
            console_output=False,  # Для консольного приложения выключаем логи в консоль
            file_output=config.log_file_path if config.log_to_file else None,
            colorful=config.log_colorful,
        )
        logger.info("Конфигурация успешно загружена")

        # Создание консольного приложения
        try:
            app = ConsoleApp(config)
            context.set_app(app)
        except Exception as e:
            logger.error(
                "Ошибка создания приложения",
                error=str(e),
                error_type=type(e).__name__,
            )
            print(ErrorMessages.CRITICAL_ERROR.value.format(error=str(e)))
            return 1

        # Настройка обработки сигналов для graceful shutdown
        shutdown_handler = create_shutdown_handler(context)
        signal.signal(signal.SIGINT, shutdown_handler)
        signal.signal(signal.SIGTERM, shutdown_handler)

        # Запуск приложения в отдельной задаче
        logger.info("Запуск консольного приложения")
        app_task = asyncio.create_task(app.run())
        shutdown_task = asyncio.create_task(context.wait_for_shutdown())

        # Ожидание завершения приложения или сигнала остановки
        done, pending = await asyncio.wait(
            [app_task, shutdown_task], return_when=asyncio.FIRST_COMPLETED
        )

        # Если получен сигнал остановки, останавливаем приложение
        if shutdown_task in done:
            logger.info("Обработка сигнала остановки")
            await context.shutdown()
            # Ожидаем завершения app.run()
            try:
                await asyncio.wait_for(app_task, timeout=5.0)
            except TimeoutError:
                logger.warning("Таймаут при ожидании завершения приложения")
                app_task.cancel()

        logger.info("Приложение завершило работу")

    except KeyboardInterrupt:
        logger.info("Приложение прервано пользователем (Ctrl+C)")
        print(InfoMessages.USER_STOPPED.value)
        return 0

    except Exception as e:
        logger.error("Критическая ошибка", error=str(e), error_type=type(e).__name__)
        print(ErrorMessages.CRITICAL_ERROR.value.format(error=str(e)))
        return 1

    finally:
        logger.info("Очистка ресурсов")
        context.cleanup()

    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(InfoMessages.USER_STOPPED.value)
        sys.exit(0)
    except Exception as e:
        print(ErrorMessages.FATAL_ERROR.value.format(error=str(e)))
        sys.exit(1)
