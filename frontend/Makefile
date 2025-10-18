# Frontend Makefile
# Команды для управления frontend проектом

.PHONY: help install dev build start lint format type-check clean

# Показать справку
help:
	@echo "Frontend команды:"
	@echo "  install     - Установить зависимости"
	@echo "  dev         - Запустить dev сервер"
	@echo "  build       - Сборка production"
	@echo "  start       - Запуск production сервера"
	@echo "  lint        - Линтинг кода"
	@echo "  format      - Форматирование кода"
	@echo "  type-check  - Проверка TypeScript типов"
	@echo "  clean       - Очистка временных файлов"

# Установить зависимости
install:
	@echo "Установка зависимостей frontend..."
	pnpm install

# Запустить dev сервер
dev:
	@echo "Запуск frontend dev сервера..."
	@echo "Frontend будет доступно по адресу: http://localhost:3000"
	pnpm dev

# Сборка production
build:
	@echo "Сборка frontend production..."
	pnpm build

# Запуск production сервера
start:
	@echo "Запуск frontend production сервера..."
	pnpm start

# Линтинг кода
lint:
	@echo "Линтинг frontend кода..."
	pnpm lint

# Форматирование кода
format:
	@echo "Форматирование frontend кода..."
	pnpm format

# Проверка TypeScript типов
type-check:
	@echo "Проверка TypeScript типов..."
	pnpm type-check

# Очистка временных файлов
clean:
	@echo "Очистка временных файлов frontend..."
	rm -rf .next
	rm -rf node_modules
	rm -rf out
	rm -rf .pnpm-store
