# LLM-ассистент Telegram-бот
# Makefile для управления проектом

.PHONY: help install run test clean lint format type-check quality venv install-frontend run-frontend build-frontend lint-frontend format-frontend test-frontend

# Показать справку
help:
	@echo "Доступные команды:"
	@echo "  install     - Установить зависимости через uv"
	@echo "  run         - Запустить бота"
	@echo "  run-api     - Запустить Mock API сервер"
	@echo "  test        - Запустить тесты с покрытием"
	@echo "  test-api    - Протестировать API endpoints"
	@echo "  api-docs    - Открыть документацию API"
	@echo "  lint        - Проверить код (Ruff)"
	@echo "  format      - Форматировать код (Ruff)"
	@echo "  type-check  - Проверить типы (Mypy)"
	@echo "  quality     - Полная проверка качества"
	@echo "  clean       - Очистить временные файлы"
	@echo "  venv        - Создать виртуальное окружение"
	@echo ""
	@echo "Frontend команды:"
	@echo "  install-frontend  - Установить зависимости frontend"
	@echo "  run-frontend      - Запустить frontend dev сервер"
	@echo "  build-frontend    - Сборка frontend production"
	@echo "  lint-frontend     - Линтинг frontend кода"
	@echo "  format-frontend   - Форматирование frontend кода"
	@echo "  test-frontend     - Запуск frontend тестов"

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

# Запустить API сервер с Chat
run-api:
	@echo "Запуск API сервера с Chat..."
	@echo "API будет доступно по адресу: http://localhost:8000"
	@echo "Документация: http://localhost:8000/docs"
	@echo "Chat API: http://localhost:8000/api/chat/message"
	python -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload

# Протестировать API endpoints
test-api:
	@echo "Тестирование API endpoints..."
	@echo ""
	@echo "=== GET /api/stats?period=day ==="
	@curl -s -X GET "http://localhost:8000/api/stats?period=day" | python -m json.tool
	@echo ""
	@echo "=== GET /api/stats?period=week ==="
	@curl -s -X GET "http://localhost:8000/api/stats?period=week" | python -m json.tool
	@echo ""
	@echo "=== GET /api/stats?period=month ==="
	@curl -s -X GET "http://localhost:8000/api/stats?period=month" | python -m json.tool

# Открыть документацию API
api-docs:
	@echo "Открытие документации API в браузере..."
	@start http://localhost:8000/docs

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

# Frontend команды

# Установить зависимости frontend
install-frontend:
	@echo "Установка зависимостей frontend..."
	@cd frontend && pnpm install

# Запустить frontend dev сервер
run-frontend:
	@echo "Запуск frontend dev сервера..."
	@echo "Frontend будет доступно по адресу: http://localhost:3000"
	@cd frontend && pnpm dev

# Сборка frontend production
build-frontend:
	@echo "Сборка frontend production..."
	@cd frontend && pnpm build

# Линтинг frontend кода
lint-frontend:
	@echo "Линтинг frontend кода..."
	@cd frontend && pnpm lint

# Форматирование frontend кода
format-frontend:
	@echo "Форматирование frontend кода..."
	@cd frontend && pnpm format

# Запуск frontend тестов
test-frontend:
	@echo "Запуск frontend тестов..."
	@cd frontend && pnpm test
