# LLM-ассистент Telegram-бот
# Makefile для управления проектом

.PHONY: help install run test clean lint format type-check quality venv

# Показать справку
help:
	@echo "Доступные команды:"
	@echo "  install     - Установить зависимости через uv"
	@echo "  run         - Запустить бота"
	@echo "  test        - Запустить тесты с покрытием"
	@echo "  lint        - Проверить код (Ruff)"
	@echo "  format      - Форматировать код (Ruff)"
	@echo "  type-check  - Проверить типы (Mypy)"
	@echo "  quality     - Полная проверка качества"
	@echo "  clean       - Очистить временные файлы"
	@echo "  venv        - Создать виртуальное окружение"

# Создать виртуальное окружение
venv:
	@echo "Создание виртуального окружения через uv..."
	uv venv

# Установить зависимости
install: venv
	@echo "Установка зависимостей через uv..."
	uv pip install -e .
	uv pip install -e ".[dev]"

# Запустить бота
run:
	@echo "Запуск бота..."
	@powershell -ExecutionPolicy Bypass -File run.ps1

# Запустить тесты с покрытием
test:
	@echo "Запуск тестов через uv..."
	uv run pytest

# Проверить код через Ruff
lint:
	@echo "Проверка кода через Ruff..."
	uv run ruff check src tests

# Форматировать код через Ruff
format:
	@echo "Форматирование кода через Ruff..."
	uv run ruff format src tests
	uv run ruff check --fix src tests

# Проверить типизацию через Mypy
type-check:
	@echo "Проверка типизации через Mypy..."
	uv run mypy src

# Полная проверка качества
quality:
	@echo "=========================================="
	@echo "Полная проверка качества кода"
	@echo "=========================================="
	@echo ""
	@echo "1/4 Форматирование кода..."
	@$(MAKE) format
	@echo ""
	@echo "2/4 Проверка стиля..."
	@$(MAKE) lint
	@echo ""
	@echo "3/4 Проверка типов..."
	@$(MAKE) type-check
	@echo ""
	@echo "4/4 Запуск тестов..."
	@$(MAKE) test
	@echo ""
	@echo "=========================================="
	@echo "✅ Все проверки завершены!"
	@echo "=========================================="

# Очистить временные файлы
clean:
	@echo "Очистка временных файлов..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	rm -rf .venv
