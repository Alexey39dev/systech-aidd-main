# LLM-ассистент Telegram-бот
# Makefile для управления проектом

.PHONY: help install run test clean lint format

# Показать справку
help:
	@echo "Доступные команды:"
	@echo "  install  - Установить зависимости"
	@echo "  run      - Запустить бота"
	@echo "  test     - Запустить тесты"
	@echo "  clean    - Очистить временные файлы"
	@echo "  lint     - Проверить код"
	@echo "  format   - Форматировать код"

# Установить зависимости
install:
	@echo "Установка зависимостей..."
	python -m pip install -e .
	python -m pip install -e ".[dev]"

# Запустить бота
run:
	@echo "Запуск бота..."
	python -m src.bot

# Запустить тесты
test:
	@echo "Запуск тестов..."
	pytest

# Очистить временные файлы
clean:
	@echo "Очистка временных файлов..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +

# Проверить код
lint:
	@echo "Проверка кода..."
	python -m flake8 src tests

# Форматировать код
format:
	@echo "Форматирование кода..."
	python -m black src tests
