"""Консольный интерфейс для LLM-ассистента."""

import asyncio
from typing import Optional
from openai import APIError, APIConnectionError, RateLimitError, APITimeoutError

from .config import Config
from .llm_client import LLMClient
from .dialog_manager import DialogManager
from .logger import get_logger


class ConsoleApp:
    """Консольное приложение для взаимодействия с LLM."""

    def __init__(self, config: Config):
        """
        Инициализация консольного приложения.

        Args:
            config: Конфигурация приложения
        """
        self.config = config
        self.logger = get_logger("console")
        self.llm_client = LLMClient(config)
        self.dialog_manager = DialogManager(max_history=config.max_history)
        self.is_running = False

    async def get_response(self, user_message: str) -> str:
        """
        Получение ответа от LLM с улучшенной обработкой ошибок.

        Args:
            user_message: Сообщение пользователя

        Returns:
            Ответ ассистента
        """
        try:
            # Получаем ответ от LLM с учетом истории
            response = await self.llm_client.get_response(
                user_message=user_message,
                system_prompt=self.config.system_prompt,
                conversation_history=self.dialog_manager.get_history()
            )
            
            # Добавляем в историю после успешного получения ответа
            self.dialog_manager.add_user_message(user_message)
            self.dialog_manager.add_assistant_message(response)
            
            return response
        
        except RateLimitError as e:
            self.logger.error("Rate limit превышен", error=str(e))
            return (
                "Извините, превышен лимит запросов к сервису. "
                "Пожалуйста, подождите немного и попробуйте снова."
            )
            
        except APIConnectionError as e:
            self.logger.error("Ошибка подключения к API", error=str(e))
            return (
                "Извините, не удалось подключиться к серверу. "
                "Проверьте подключение к интернету и попробуйте снова."
            )
            
        except APITimeoutError as e:
            self.logger.error("Таймаут API", error=str(e))
            return (
                "Извините, сервер не ответил вовремя. "
                "Попробуйте отправить запрос еще раз."
            )
            
        except APIError as e:
            self.logger.error("Ошибка API", error=str(e), status_code=getattr(e, 'status_code', None))
            if hasattr(e, 'status_code'):
                if 400 <= e.status_code < 500:
                    return (
                        f"Извините, произошла ошибка запроса (код {e.status_code}). "
                        "Попробуйте перефразировать ваш вопрос."
                    )
                elif 500 <= e.status_code < 600:
                    return (
                        f"Извините, на сервере произошла ошибка (код {e.status_code}). "
                        "Попробуйте позже."
                    )
            return "Извините, произошла ошибка при обращении к сервису."
            
        except KeyboardInterrupt:
            # Пробрасываем дальше для корректного завершения
            raise
            
        except Exception as e:
            self.logger.error("Неожиданная ошибка получения ответа", error=str(e), error_type=type(e).__name__)
            return (
                "Извините, произошла неожиданная ошибка. "
                "Попробуйте еще раз или обратитесь к администратору."
            )

    def clear_history(self) -> None:
        """Очистка истории диалога."""
        self.dialog_manager.clear_history()

    def print_history(self) -> None:
        """Вывод истории диалога."""
        history = self.dialog_manager.get_history()
        
        if not history:
            print("\nИстория диалога пуста.\n")
            return
        
        print("\n" + "-" * 70)
        print("История диалога:")
        print("-" * 70)
        
        for i, msg in enumerate(history, 1):
            role = "Вы" if msg["role"] == "user" else "Ассистент"
            content = msg["content"]
            
            # Ограничиваем длину для удобства чтения
            if len(content) > 100:
                content = content[:97] + "..."
            
            print(f"{i}. {role}: {content}")
        
        print("-" * 70)
        print(f"Всего сообщений: {len(history)}")
        print("-" * 70 + "\n")

    def print_stats(self) -> None:
        """Вывод статистики диалога."""
        stats = self.dialog_manager.get_conversation_summary()
        
        print("\n" + "-" * 70)
        print("Статистика диалога:")
        print("-" * 70)
        print(f"  Всего сообщений: {stats['total_messages']}")
        print(f"  Ваших сообщений: {stats['user_messages']}")
        print(f"  Ответов ассистента: {stats['assistant_messages']}")
        print(f"  Макс. история (пар): {stats['max_history']}")
        
        # Процент заполненности истории
        max_messages = stats['max_history'] * 2
        fill_percent = (stats['total_messages'] / max_messages * 100) if max_messages > 0 else 0
        print(f"  Заполненность истории: {fill_percent:.1f}%")
        
        print("-" * 70 + "\n")

    def print_welcome(self) -> None:
        """Вывод приветственного сообщения."""
        print("\n" + "=" * 70)
        print("LLM-Ассистент через консоль")
        print("=" * 70)
        print("\nДоступные команды:")
        print("  /help     - Показать справку с примерами")
        print("  /history  - Показать историю диалога")
        print("  /stats    - Показать статистику диалога")
        print("  /clear    - Очистить историю диалога")
        print("  /exit     - Выйти из приложения")
        print("\nПросто введите ваш вопрос и нажмите Enter для отправки.")
        print("=" * 70 + "\n")

    def print_help(self) -> None:
        """Вывод справки с примерами."""
        print("\n" + "-" * 70)
        print("Справка по командам:")
        print("-" * 70)
        print("\nОсновные команды:")
        print("  /help     - Показать эту справку")
        print("  /history  - Показать историю диалога")
        print("  /stats    - Показать статистику (количество сообщений)")
        print("  /clear    - Очистить историю диалога")
        print("  /exit     - Выйти из приложения")
        
        print("\nПримеры использования:")
        print("  Вы: Привет! Как дела?")
        print("  Ассистент: [ответ ассистента]")
        print()
        print("  Вы: /history")
        print("  [показывает историю ваших сообщений]")
        print()
        print("  Вы: /clear")
        print("  [очищает историю диалога]")
        
        print(f"\nТекущая конфигурация:")
        print(f"  Модель: {self.config.llm_model}")
        print(f"  Температура: {self.config.llm_temperature}")
        print(f"  Макс. токенов ответа: {self.config.llm_max_tokens}")
        print(f"  Макс. история (пар): {self.config.max_history}")
        print("-" * 70 + "\n")

    async def handle_command(self, command: str) -> bool:
        """
        Обработка команды.

        Args:
            command: Команда пользователя

        Returns:
            True если нужно продолжить работу, False для выхода
        """
        command = command.lower().strip()
        
        if command == "/exit":
            print("\nДо свидания!")
            return False
        elif command == "/help":
            self.print_help()
        elif command == "/history":
            self.print_history()
        elif command == "/stats":
            self.print_stats()
        elif command == "/clear":
            stats = self.dialog_manager.get_conversation_summary()
            self.clear_history()
            print(f"История диалога очищена (удалено сообщений: {stats['total_messages']}).\n")
        else:
            print(f"Неизвестная команда: {command}")
            print("Введите /help для просмотра доступных команд.\n")
        
        return True

    async def run(self) -> None:
        """Запуск консольного приложения."""
        self.is_running = True
        self.print_welcome()
        
        try:
            while self.is_running:
                try:
                    # Получение ввода пользователя
                    user_input = await asyncio.get_event_loop().run_in_executor(
                        None, input, "Вы: "
                    )
                    
                    # Проверка на пустой ввод
                    if not user_input.strip():
                        continue
                    
                    # Обработка команд
                    if user_input.startswith("/"):
                        should_continue = await self.handle_command(user_input)
                        if not should_continue:
                            break
                        continue
                    
                    # Получение и вывод ответа
                    print("\nАссистент: ", end="", flush=True)
                    response = await self.get_response(user_input)
                    print(response + "\n")
                    
                except KeyboardInterrupt:
                    print("\n\nПолучен сигнал прерывания. До свидания!")
                    break
                except EOFError:
                    print("\n\nДо свидания!")
                    break
                    
        except Exception as e:
            self.logger.error("Критическая ошибка в консольном приложении", error=str(e))
            print(f"\nКритическая ошибка: {str(e)}")
        finally:
            self.is_running = False

    async def stop(self) -> None:
        """Остановка консольного приложения."""
        self.is_running = False

