"""Консольный интерфейс для LLM-ассистента."""

import asyncio
from pathlib import Path

from .config import Config
from .dialog_manager import DialogManager
from .exceptions import LLMError
from .llm_client import LLMClient
from .logger import get_logger
from .messages import ErrorMessages, InfoMessages
from .role_manager import RoleManager


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
        self.role_manager = RoleManager(
            Path(config.system_prompt_file) if config.system_prompt_file else None
        )
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
                conversation_history=self.dialog_manager.get_history(),
            )

            # Добавляем в историю после успешного получения ответа
            self.dialog_manager.add_user_message(user_message)
            self.dialog_manager.add_assistant_message(response)

            return response

        except LLMError as e:
            # Обработка всех LLM ошибок
            self.logger.error(
                "Ошибка работы с LLM",
                error=str(e),
                error_type=type(e).__name__,
                details=e.details,
            )

            # Пытаемся получить fallback ответ
            try:
                return await self.llm_client.get_fallback_response(user_message)
            except Exception as fallback_error:
                self.logger.error(
                    "Не удалось получить fallback ответ",
                    error=str(fallback_error),
                )
            return ErrorMessages.LLM_ERROR.value

        except KeyboardInterrupt:
            # Пробрасываем дальше для корректного завершения
            raise

        except Exception as e:
            self.logger.error(
                "Неожиданная ошибка получения ответа",
                error=str(e),
                error_type=type(e).__name__,
            )
            return ErrorMessages.UNEXPECTED_ERROR.value

    def clear_history(self) -> None:
        """Очистка истории диалога."""
        self.dialog_manager.clear_history()

    def print_history(self) -> None:
        """Вывод истории диалога."""
        history = self.dialog_manager.get_history()

        if not history:
            print(InfoMessages.HISTORY_EMPTY.value)
            return

        print("\n" + InfoMessages.SEPARATOR_SHORT.value)
        print(InfoMessages.HISTORY_HEADER.value)
        print(InfoMessages.SEPARATOR_SHORT.value)

        for i, msg in enumerate(history, 1):
            role = "Вы" if msg["role"] == "user" else "Ассистент"
            content = msg["content"]

            # Ограничиваем длину для удобства чтения
            if len(content) > 100:
                content = content[:97] + "..."

            print(f"{i}. {role}: {content}")

        print(InfoMessages.SEPARATOR_SHORT.value)
        print(f"Всего сообщений: {len(history)}")
        print(InfoMessages.SEPARATOR_SHORT.value + "\n")

    def print_stats(self) -> None:
        """Вывод статистики диалога."""
        stats = self.dialog_manager.get_conversation_summary()

        print("\n" + InfoMessages.SEPARATOR_SHORT.value)
        print(InfoMessages.STATS_HEADER.value)
        print(InfoMessages.SEPARATOR_SHORT.value)
        print(InfoMessages.STATS_TOTAL.value.format(total=stats["total_messages"]))
        print(InfoMessages.STATS_USER.value.format(user=stats["user_messages"]))
        print(InfoMessages.STATS_ASSISTANT.value.format(assistant=stats["assistant_messages"]))
        print(InfoMessages.STATS_MAX_HISTORY.value.format(max_history=stats["max_history"]))

        # Процент заполненности истории
        max_pairs = stats["max_history"]
        current_pairs = stats["total_messages"] // 2
        usage_percent = (current_pairs / max_pairs * 100) if max_pairs > 0 else 0
        print(
            InfoMessages.STATS_USAGE.value.format(
                usage_percent=f"{usage_percent:.1f}",
                current=current_pairs,
                max_pairs=max_pairs,
            )
        )

        print(InfoMessages.SEPARATOR_SHORT.value + "\n")

    def print_role_info(self) -> None:
        """Вывод информации о текущей роли."""
        role_info = self.role_manager.get_role_info()

        print("\n" + InfoMessages.SEPARATOR_SHORT.value)
        print("📋 Текущая роль:")
        print(InfoMessages.SEPARATOR_SHORT.value)
        print(f"Название: {role_info['title']}")
        print(f"Описание: {role_info['description']}")
        print(f"Источник: {role_info['source']}")
        print(InfoMessages.SEPARATOR_SHORT.value + "\n")

    def print_welcome(self) -> None:
        """Вывод приветственного сообщения."""
        print("\n" + InfoMessages.SEPARATOR.value)
        print(InfoMessages.WELCOME_HEADER.value)
        print(InfoMessages.SEPARATOR.value)
        print(InfoMessages.AVAILABLE_COMMANDS.value)
        print(InfoMessages.CMD_HELP.value)
        print(InfoMessages.CMD_HISTORY.value)
        print(InfoMessages.CMD_STATS.value)
        print("  /role     - Показать информацию о текущей роли")
        print(InfoMessages.CMD_CLEAR.value)
        print(InfoMessages.CMD_EXIT.value)
        print("\nПросто введите ваш вопрос и нажмите Enter для отправки.")
        print(InfoMessages.SEPARATOR.value + "\n")

    def print_help(self) -> None:
        """Вывод справки с примерами."""
        print("\n" + InfoMessages.SEPARATOR_SHORT.value)
        print(InfoMessages.HELP_HEADER.value)
        print(InfoMessages.SEPARATOR_SHORT.value)
        print(InfoMessages.MAIN_COMMANDS.value)
        print(InfoMessages.CMD_HELP.value)
        print(InfoMessages.CMD_HISTORY.value)
        print(InfoMessages.CMD_STATS.value)
        print("  /role     - Показать информацию о текущей роли")
        print(InfoMessages.CMD_CLEAR.value)
        print(InfoMessages.CMD_EXIT.value)

        print(InfoMessages.EXAMPLES_HEADER.value)
        print(InfoMessages.EXAMPLE_1.value)
        print(InfoMessages.EXAMPLE_2.value)
        print(InfoMessages.EXAMPLE_3.value)

        print(InfoMessages.SETTINGS_HEADER.value)
        print(InfoMessages.SETTING_MODEL.value.format(model=self.config.llm_model))
        print(InfoMessages.SETTING_TEMP.value.format(temperature=self.config.llm_temperature))
        print(InfoMessages.SETTING_MAX_TOKENS.value.format(max_tokens=self.config.llm_max_tokens))
        print(InfoMessages.SETTING_MAX_HISTORY.value.format(max_history=self.config.max_history))
        print(InfoMessages.SEPARATOR_SHORT.value + "\n")

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
        elif command == "/role":
            self.print_role_info()
        elif command == "/clear":
            stats = self.dialog_manager.get_conversation_summary()
            self.clear_history()
            print(InfoMessages.HISTORY_CLEARED.value.format(count=stats["total_messages"]))
        else:
            print(ErrorMessages.UNKNOWN_COMMAND.value.format(command=command))
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
                    user_input = await asyncio.get_event_loop().run_in_executor(None, input, "Вы: ")

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
