"""Консольный интерфейс для LLM-ассистента."""

import asyncio
from typing import Optional

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
        Получение ответа от LLM.

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
            
        except Exception as e:
            self.logger.error("Ошибка получения ответа от LLM", error=str(e))
            return "Извините, произошла ошибка при обработке вашего запроса."

    def clear_history(self) -> None:
        """Очистка истории диалога."""
        self.dialog_manager.clear_history()

    def print_welcome(self) -> None:
        """Вывод приветственного сообщения."""
        print("\n" + "=" * 70)
        print("LLM-Ассистент через консоль")
        print("=" * 70)
        print("\nДоступные команды:")
        print("  /help    - Показать эту справку")
        print("  /clear   - Очистить историю диалога")
        print("  /exit    - Выйти из приложения")
        print("\nПросто введите ваш вопрос и нажмите Enter для отправки.")
        print("=" * 70 + "\n")

    def print_help(self) -> None:
        """Вывод справки."""
        print("\n" + "-" * 70)
        print("Справка по командам:")
        print("-" * 70)
        print("  /help    - Показать эту справку")
        print("  /clear   - Очистить историю диалога")
        print("  /exit    - Выйти из приложения")
        print(f"\nТекущая конфигурация:")
        print(f"  Модель: {self.config.llm_model}")
        print(f"  Температура: {self.config.llm_temperature}")
        print(f"  Макс. токенов: {self.config.llm_max_tokens}")
        print(f"  Макс. история: {self.config.max_history}")
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

