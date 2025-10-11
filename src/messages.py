"""Сообщения для пользователя."""

from enum import Enum


class ErrorMessages(str, Enum):
    """Сообщения об ошибках для пользователя."""

    # Ошибки LLM
    LLM_ERROR = "Извините, произошла ошибка при обращении к сервису."
    UNEXPECTED_ERROR = (
        "Извините, произошла неожиданная ошибка. "
        "Попробуйте еще раз или обратитесь к администратору."
    )

    # Ошибки конфигурации
    CONFIG_ERROR = "\nОшибка конфигурации:"
    ENV_NOT_FOUND = "\nОшибка: файл .env не найден."
    ENV_INSTRUCTION = "Создайте файл .env на основе .env.example"
    CONFIG_CHECK_PARAMS = (
        "\nПроверьте файл .env и убедитесь, что все обязательные параметры заданы."
    )

    # Ошибки приложения
    CRITICAL_ERROR = "\nКритическая ошибка: {error}"
    FATAL_ERROR = "\nФатальная ошибка: {error}"

    # Команды
    UNKNOWN_COMMAND = "Неизвестная команда: {command}"


class InfoMessages(str, Enum):
    """Информационные сообщения."""

    # Приветствие и справка
    WELCOME_HEADER = "LLM-Ассистент через консоль"
    SEPARATOR = "=" * 70
    SEPARATOR_SHORT = "-" * 70
    AVAILABLE_COMMANDS = "\nДоступные команды:"
    HELP_HEADER = "Справка по командам:"
    MAIN_COMMANDS = "\nОсновные команды:"

    # История диалога
    HISTORY_EMPTY = "\nИстория диалога пуста.\n"
    HISTORY_HEADER = "История диалога:"
    HISTORY_CLEARED = "История диалога очищена (удалено сообщений: {count}).\n"

    # Завершение
    SHUTDOWN_SIGNAL = "\n\nПолучен сигнал завершения. Завершаю работу..."
    USER_STOPPED = "\n\nПриложение остановлено пользователем"

    # Команды (описания)
    CMD_HELP = "  /help     - Показать справку с примерами"
    CMD_HISTORY = "  /history  - Показать историю диалога"
    CMD_STATS = "  /stats    - Показать статистику диалога"
    CMD_CLEAR = "  /clear    - Очистить историю диалога"
    CMD_EXIT = "  /exit     - Выход из программы"

    # Примеры
    EXAMPLES_HEADER = "\nПримеры вопросов:"
    EXAMPLE_1 = '  "Напиши функцию сортировки на Python"'
    EXAMPLE_2 = '  "Объясни что такое async/await"'
    EXAMPLE_3 = '  "Как работает декоратор в Python?"'

    # Настройки
    SETTINGS_HEADER = "\nТекущие настройки:"
    SETTING_MODEL = "  Модель: {model}"
    SETTING_TEMP = "  Температура: {temperature}"
    SETTING_MAX_TOKENS = "  Макс. токенов ответа: {max_tokens}"
    SETTING_MAX_HISTORY = "  Макс. история (пар): {max_history}"

    # Статистика
    STATS_HEADER = "Статистика диалога:"
    STATS_TOTAL = "  Всего сообщений: {total}"
    STATS_USER = "  Ваших сообщений: {user}"
    STATS_ASSISTANT = "  Ответов ассистента: {assistant}"
    STATS_MAX_HISTORY = "  Макс. история (пар): {max_history}"
    STATS_USAGE = "  Заполнено: {usage_percent}% ({current} из {max_pairs} пар)"


class FallbackMessages(str, Enum):
    """Fallback ответы при ошибках LLM."""

    FALLBACK_1 = "Извините, у меня временные технические проблемы. Попробуйте позже."
    FALLBACK_2 = "К сожалению, я не могу ответить сейчас. Обратитесь позже."
    FALLBACK_3 = "Произошла ошибка при обработке вашего запроса. Попробуйте еще раз."
    FALLBACK_4 = (
        "Сейчас у меня проблемы с подключением к сервису. Попробуйте через несколько минут."
    )

    @classmethod
    def get_all(cls) -> list[str]:
        """Получить все fallback сообщения как список.

        Returns:
            Список всех fallback сообщений
        """
        return [msg.value for msg in cls]
