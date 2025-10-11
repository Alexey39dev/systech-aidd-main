"""Тесты для модуля сообщений."""

from src.messages import ErrorMessages, FallbackMessages, InfoMessages


def test_error_messages_exist():
    """Тест что все сообщения об ошибках определены."""
    assert hasattr(ErrorMessages, "LLM_ERROR")
    assert hasattr(ErrorMessages, "UNEXPECTED_ERROR")
    assert hasattr(ErrorMessages, "CONFIG_ERROR")
    assert hasattr(ErrorMessages, "ENV_NOT_FOUND")
    assert hasattr(ErrorMessages, "ENV_INSTRUCTION")
    assert hasattr(ErrorMessages, "CONFIG_CHECK_PARAMS")
    assert hasattr(ErrorMessages, "CRITICAL_ERROR")
    assert hasattr(ErrorMessages, "FATAL_ERROR")
    assert hasattr(ErrorMessages, "UNKNOWN_COMMAND")


def test_info_messages_exist():
    """Тест что все информационные сообщения определены."""
    assert hasattr(InfoMessages, "WELCOME_HEADER")
    assert hasattr(InfoMessages, "SEPARATOR")
    assert hasattr(InfoMessages, "SEPARATOR_SHORT")
    assert hasattr(InfoMessages, "AVAILABLE_COMMANDS")
    assert hasattr(InfoMessages, "HELP_HEADER")
    assert hasattr(InfoMessages, "MAIN_COMMANDS")
    assert hasattr(InfoMessages, "HISTORY_EMPTY")
    assert hasattr(InfoMessages, "HISTORY_HEADER")
    assert hasattr(InfoMessages, "HISTORY_CLEARED")
    assert hasattr(InfoMessages, "SHUTDOWN_SIGNAL")
    assert hasattr(InfoMessages, "USER_STOPPED")
    assert hasattr(InfoMessages, "CMD_HELP")
    assert hasattr(InfoMessages, "CMD_HISTORY")
    assert hasattr(InfoMessages, "CMD_STATS")
    assert hasattr(InfoMessages, "CMD_CLEAR")
    assert hasattr(InfoMessages, "CMD_EXIT")


def test_fallback_messages_exist():
    """Тест что все fallback сообщения определены."""
    assert hasattr(FallbackMessages, "FALLBACK_1")
    assert hasattr(FallbackMessages, "FALLBACK_2")
    assert hasattr(FallbackMessages, "FALLBACK_3")
    assert hasattr(FallbackMessages, "FALLBACK_4")


def test_error_messages_are_strings():
    """Тест что все сообщения об ошибках являются строками."""
    assert isinstance(ErrorMessages.LLM_ERROR.value, str)
    assert isinstance(ErrorMessages.UNEXPECTED_ERROR.value, str)
    assert isinstance(ErrorMessages.CONFIG_ERROR.value, str)
    assert isinstance(ErrorMessages.UNKNOWN_COMMAND.value, str)


def test_info_messages_are_strings():
    """Тест что все информационные сообщения являются строками."""
    assert isinstance(InfoMessages.WELCOME_HEADER.value, str)
    assert isinstance(InfoMessages.HISTORY_EMPTY.value, str)
    assert isinstance(InfoMessages.SHUTDOWN_SIGNAL.value, str)


def test_fallback_messages_are_strings():
    """Тест что все fallback сообщения являются строками."""
    assert isinstance(FallbackMessages.FALLBACK_1.value, str)
    assert isinstance(FallbackMessages.FALLBACK_2.value, str)
    assert isinstance(FallbackMessages.FALLBACK_3.value, str)
    assert isinstance(FallbackMessages.FALLBACK_4.value, str)


def test_fallback_messages_get_all():
    """Тест метода get_all для fallback сообщений."""
    all_messages = FallbackMessages.get_all()

    assert isinstance(all_messages, list)
    assert len(all_messages) == 4
    assert all(isinstance(msg, str) for msg in all_messages)
    assert FallbackMessages.FALLBACK_1.value in all_messages
    assert FallbackMessages.FALLBACK_2.value in all_messages
    assert FallbackMessages.FALLBACK_3.value in all_messages
    assert FallbackMessages.FALLBACK_4.value in all_messages


def test_error_messages_with_placeholders():
    """Тест что сообщения с плейсхолдерами форматируются корректно."""
    formatted = ErrorMessages.UNKNOWN_COMMAND.value.format(command="/test")
    assert "/test" in formatted
    assert "Неизвестная команда" in formatted

    formatted = ErrorMessages.CRITICAL_ERROR.value.format(error="Test error")
    assert "Test error" in formatted


def test_info_messages_with_placeholders():
    """Тест что информационные сообщения с плейсхолдерами форматируются корректно."""
    formatted = InfoMessages.HISTORY_CLEARED.value.format(count=5)
    assert "5" in formatted

    formatted = InfoMessages.STATS_TOTAL.value.format(total=10)
    assert "10" in formatted

    formatted = InfoMessages.SETTING_MODEL.value.format(model="gpt-4")
    assert "gpt-4" in formatted


def test_separator_length():
    """Тест что сепараторы имеют правильную длину."""
    assert len(InfoMessages.SEPARATOR.value) == 70
    assert len(InfoMessages.SEPARATOR_SHORT.value) == 70


def test_messages_not_empty():
    """Тест что ни одно сообщение не является пустой строкой."""
    for msg in ErrorMessages:
        assert msg.value.strip() != ""

    for msg in InfoMessages:
        assert msg.value.strip() != ""

    for msg in FallbackMessages:
        assert msg.value.strip() != ""


def test_error_messages_content():
    """Тест содержимого некоторых ключевых сообщений об ошибках."""
    assert "Извините" in ErrorMessages.LLM_ERROR.value
    assert "Извините" in ErrorMessages.UNEXPECTED_ERROR.value


def test_info_messages_content():
    """Тест содержимого некоторых ключевых информационных сообщений."""
    assert (
        "Добро пожаловать" in InfoMessages.WELCOME_HEADER.value
        or "LLM" in InfoMessages.WELCOME_HEADER.value
    )
    assert "История" in InfoMessages.HISTORY_HEADER.value
    assert "Справка" in InfoMessages.HELP_HEADER.value


def test_fallback_messages_content():
    """Тест содержимого fallback сообщений."""
    all_messages = FallbackMessages.get_all()
    for msg in all_messages:
        # Все fallback сообщения должны содержать вежливые извинения
        assert any(word in msg.lower() for word in ["извините", "сожалению", "ошибка", "проблем"])
