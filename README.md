# LLM-ассистент через консоль

Простой LLM-ассистент с консольным интерфейсом для ведения диалога и ответов на вопросы пользователя с заданной ролью через системный промпт.

## 🐳 Quick Start

**Запуск всех сервисов одной командой:**
```bash
docker-compose up -d
```

**Доступ к сервисам:**
- 🌐 **API:** http://localhost:8000
- 📊 **API Docs:** http://localhost:8000/docs  
- 💻 **Frontend:** http://localhost:3000
- 📈 **Dashboard:** http://localhost:3000/dashboard

**Остановка:**
```bash
docker-compose down
```

> 📖 **Подробная документация:** [Запуск через Docker](#-запуск-через-docker)

---

## 🎉 Новое: Frontend Dashboard

**Sprint FS-003 ПОЛНОСТЬЮ ЗАВЕРШЕН!** ✅ Добавлен полнофункциональный веб-дашборд для мониторинга статистики диалогов.

📖 **Документация**: [frontend/DASHBOARD-READY.md](frontend/DASHBOARD-READY.md) | [Итоги спринта](frontend/doc/SPRINT-FS003-FINAL-COMPLETION.md)  
🚀 **Запуск**: `make run-api` + `cd frontend && npm run dev`  
🌐 **URL**: http://localhost:3000/dashboard

**Возможности:**
- 📊 Метрики диалогов (всего, активные пользователи, средняя длина, успешность)
- 📈 **Area Chart** с линией тренда и градиентом
- 💬 Список последних диалогов
- 👥 Топ-10 активных пользователей с иконками
- 🔄 Фильтрация по периодам (Day/Week/Month)
- 🌙 **Тёмная тема** по умолчанию
- 📱 **Адаптивный дизайн** для всех устройств
- 🎨 **100% соответствие** [shadcn/ui dashboard-01](https://ui.shadcn.com/blocks#dashboard-01)

---

## 🚀 Быстрый старт

### Предварительные требования

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) - современный менеджер пакетов Python
- OpenRouter API Key (получить на [openrouter.ai](https://openrouter.ai))

### Установка

1. **Установите uv (если еще не установлен):**
   
   Windows:
   ```powershell
   winget install --id=astral-sh.uv -e
   ```
   
   macOS/Linux:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Клонируйте репозиторий:**
   ```bash
   git clone <repository-url>
   cd systech-aidd
   ```

3. **Установите зависимости:**
   ```bash
   make install
   ```
   
   Или напрямую через uv:
   ```bash
   uv venv
   uv pip install -e .
   uv pip install -e ".[dev]"
   ```

4. **Настройте конфигурацию:**
   ```bash
   cp .env.example .env
   # Отредактируйте .env файл, добавив ваши токены
   ```

5. **Запустите приложение:**
   ```bash
   make run
   ```
   
   Или напрямую:
   ```bash
   .\run.ps1
   ```

## 🐳 Запуск через Docker

### Быстрый старт

1. **Создайте .env файл:**
   ```bash
   cp .env.example .env
   # Отредактируйте .env, добавьте OPENROUTER_API_KEY
   ```

2. **Запустите все сервисы:**
   ```bash
   docker-compose up
   ```

3. **Доступ к сервисам:**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Frontend Dashboard: http://localhost:3000/dashboard
   - Frontend Chat: http://localhost:3000/chat
   - PgAdmin: http://localhost:5050 (профиль tools: `docker-compose --profile tools up`)

### Команды Docker

```bash
# Запустить в фоновом режиме
docker-compose up -d

# Остановить все сервисы
docker-compose down

# Пересобрать образы
docker-compose build

# Просмотр логов
docker-compose logs -f [service_name]

# Запустить миграции вручную
docker-compose run --rm migrations
```

### Структура сервисов

- `postgres` - База данных PostgreSQL 16
- `migrations` - Автоматический запуск миграций Alembic
- `bot` - Консольный AI-ассистент
- `api` - FastAPI сервер для статистики и чата
- `frontend` - Next.js веб-интерфейс
- `pgadmin` - Админ панель БД (опционально)

## 🚀 Использование образов из GitHub Container Registry

### Быстрый старт с готовыми образами

Вместо локальной сборки можно использовать готовые образы из GitHub Container Registry:

1. **Создайте .env файл:**
   ```bash
   cp .env.example .env
   # Отредактируйте .env, добавьте OPENROUTER_API_KEY
   ```

2. **Запустите сервисы из registry:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Доступ к сервисам:**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Frontend: http://localhost:3000

### Переключение между локальной сборкой и registry

**Локальная сборка (разработка):**
```bash
docker-compose up --build
```

**Образы из registry (production):**
```bash
docker-compose -f docker-compose.prod.yml up
```

### Статус сборки

![Build Status](https://github.com/[USERNAME]/systech-aidd-main/actions/workflows/build.yml/badge.svg)

### Ручное скачивание образов

```bash
# Скачать образы вручную
docker pull ghcr.io/[USERNAME]/systech-aidd-main-bot:latest
docker pull ghcr.io/[USERNAME]/systech-aidd-main-api:latest
docker pull ghcr.io/[USERNAME]/systech-aidd-main-frontend:latest

# Проверить образы
docker images | grep systech-aidd
```

**Примечание:** Заменить `[USERNAME]` на реальное имя пользователя GitHub.

## 📁 Структура проекта

```
systech-aidd/
├── src/                    # Исходный код (12 модулей)
│   ├── console.py         # ConsoleApp - консольный интерфейс
│   ├── llm_client.py      # LLMClient - клиент для LLM
│   ├── dialog_manager.py  # DialogManager - управление историей
│   ├── config.py          # Config - конфигурация приложения
│   ├── logger.py          # Logger - структурированное логирование
│   ├── main.py            # Точка входа приложения
│   ├── role_manager.py    # 🆕 RoleManager - система ролей
│   ├── exceptions.py      # Кастомные исключения (иерархия LLMError)
│   ├── retry_utils.py     # Retry логика с экспоненциальным backoff
│   ├── types.py           # TypedDict и Literal для строгой типизации
│   ├── messages.py        # Enum классы для сообщений (DRY принцип)
│   └── py.typed           # PEP 561 маркер для type hints
├── prompts/               # 🆕 Файлы промптов с метаданными
│   ├── default.txt        # Базовая роль
│   ├── tech_support.txt   # Техническая поддержка
│   └── code_reviewer.txt  # Ревью кода
├── tests/                 # Тесты (164 теста, 88.82% coverage)
│   ├── test_config.py
│   ├── test_console.py
│   ├── test_dialog_manager.py
│   ├── test_llm_client.py
│   ├── test_integration.py
│   ├── test_role_manager.py    # 🆕 Тесты системы ролей
│   ├── test_exceptions.py
│   ├── test_retry_utils.py
│   ├── test_logger.py
│   ├── test_messages.py
│   └── test_main.py
├── docs/                  # Документация
│   ├── vision.md          # Техническое видение
│   ├── configuration.md   # Руководство по конфигурации
│   ├── tasklist.md        # План разработки
│   └── baseline_metrics.md # Метрики качества кода
├── .env.example           # Пример конфигурации
├── pyproject.toml         # Конфигурация проекта (Ruff, Mypy, pytest)
├── run.ps1               # Скрипт запуска для Windows
└── Makefile              # Команды сборки и запуска
```

## ⚙️ Конфигурация

Скопируйте `.env.example` в `.env` и настройте следующие параметры:

```env
# OpenRouter API Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here

# LLM Configuration
SYSTEM_PROMPT=Ты полезный ассистент. Отвечай дружелюбно и информативно.
MAX_HISTORY=10
LLM_MODEL=openai/gpt-3.5-turbo
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1000

# Logging Configuration
LOG_LEVEL=INFO
LOG_TO_FILE=false
LOG_FILE_PATH=logs/app.log
LOG_COLORFUL=true
```

## 🛠️ Команды разработки

### Через командную строку

```bash
make install      # Установить зависимости
make run          # Запустить приложение
make test         # Запустить тесты (149 тестов, 87.59% coverage)
make quality      # 🆕 Полная проверка качества (format + lint + type-check + test)
make lint         # Проверить код (Ruff linter)
make format       # Форматировать код (Ruff formatter)
make type-check   # 🆕 Проверить типизацию (Mypy strict mode)
make clean        # Очистить временные файлы
```

### 🎯 Через UI Cursor/VS Code

Проект полностью настроен для работы через UI редактора!

**Запуск приложения:**
1. Нажмите `F5` или откройте панель Run and Debug (`Ctrl+Shift+D`)
2. Выберите конфигурацию:
   - `▶️ Запустить приложение` - обычный запуск
   - `🐛 Отладка приложения` - запуск с полной отладкой
   - `🔍 Запуск с логами DEBUG` - детальное логирование

**Запуск тестов:**

*Вариант 1: Через панель Testing*
1. Откройте панель тестов (иконка колбы в боковой панели)
2. Нажмите `▶️` для запуска всех тестов или выберите конкретные

*Вариант 2: Через Run and Debug*
1. Откройте `Ctrl+Shift+D`
2. Выберите:
   - `🧪 Запустить все тесты` - все 149 тестов
   - `🧪 Запустить тесты с покрытием` - тесты + HTML отчет
   - `🧪 Отладка текущего теста` - отладка открытого файла
   - `🧪 Отладка конкретного теста` - выделите имя и запустите

*Вариант 3: Через Tasks*
1. `Ctrl+Shift+P` → `Tasks: Run Task`
2. Выберите нужную задачу (тесты, линтинг, форматирование и др.)

**Дополнительные возможности:**
- Автоформатирование кода при сохранении (Ruff)
- Автоорганизация импортов
- Проверка типов в реальном времени (Mypy + Pylance)
- Встроенный дебаггер с точками останова

📖 **Подробное руководство:** [.vscode/README.md](.vscode/README.md)

## 💬 Использование

После запуска приложения вы увидите приветственное сообщение и приглашение ввода.

**Доступные команды:**
- `/help` - Показать справку с примерами
- `/history` - Показать историю диалога
- `/stats` - Показать статистику диалога
- `/role` - Показать информацию о текущей роли ассистента
- `/clear` - Очистить историю диалога
- `/exit` - Выйти из приложения

**Пример диалога:**
```
Вы: Привет!
Ассистент: Привет! Как я могу помочь тебе сегодня?

Вы: Расскажи про Python
Ассистент: Python - это высокоуровневый язык программирования...

Вы: /stats
Статистика диалога:
  Всего сообщений: 4
  Ваших сообщений: 2
  Ответов ассистента: 2
  Макс. история (пар): 10
  Заполненность истории: 20.0%
```

## 🎭 Система ролей

Приложение поддерживает загрузку системных промптов из файлов с метаданными. Это позволяет легко переключаться между разными ролями ассистента.

### Формат файла промпта

```
# Title: Название роли
# Description: Описание роли (может быть многострочным)

Здесь идет содержимое системного промпта...
```

### Примеры ролей

В директории `prompts/` находятся готовые примеры:

- **`default.txt`** - Общий ассистент (базовая роль)
- **`tech_support.txt`** - Техническая поддержка
- **`code_reviewer.txt`** - Ревью кода

### Использование

1. **Создайте файл промпта** в директории `prompts/`
2. **Укажите путь** в `.env`:
   ```bash
   SYSTEM_PROMPT_FILE=prompts/tech_support.txt
   ```
3. **Запустите** приложение - роль будет загружена автоматически
4. **Проверьте** текущую роль командой `/role`

**Пример вывода `/role`:**
```
----------------------------------------------------------------------
📋 Текущая роль:
----------------------------------------------------------------------
Название: Technical Support Specialist
Описание: Provides technical support, troubleshooting help, and guides users through problem resolution.
Источник: prompts\tech_support.txt
----------------------------------------------------------------------
```

### Создание собственной роли

Создайте новый файл в `prompts/`, например `my_role.txt`:

```
# Title: My Custom Assistant
# Description: A specialized assistant for my specific needs

You are a friendly assistant specialized in...
[ваши инструкции для ассистента]
```

Затем укажите его в `.env`: `SYSTEM_PROMPT_FILE=prompts/my_role.txt`

## 📚 Документация

### Разработка
- [🚀 Настройка Cursor](.vscode/SETUP_COMPLETE.md) - конфигурация UI для запуска и тестов
- [⚡ Быстрый старт](.vscode/QUICKSTART.md) - начало работы за 5 минут
- [📖 Руководство по UI](.vscode/README.md) - детальное руководство
- [📋 Конфигурация](.vscode/CONFIGURATION.md) - детали настроек

### Проектная документация
- [Идея проекта](docs/idea.md)
- [Техническое видение](docs/vision.md)
- [Правила разработки](docs/conventions.md)
- [План разработки](docs/tasklist.md)
- [Workflow](docs/workflow.md)

## 🎯 Особенности

### Основные возможности
- **Простота**: Минимальный MVP без оверинжиниринга (KISS принцип)
- **Консольный интерфейс**: Удобная работа через терминал
- **Система ролей**: Загрузка промптов из файлов с метаданными (см. `prompts/`)
- **Асинхронность**: Высокая производительность с async/await
- **Модульность**: Четкое разделение ответственности (1 класс = 1 файл)
- **Гибкость**: Легкая настройка роли ассистента через системный промпт
- **История диалога**: Контекстные ответы с учетом предыдущих сообщений
- **Управление историей**: Автоматическая обрезка при превышении лимита

### Обработка ошибок и устойчивость
- **Кастомные исключения**: Иерархия LLMError для точной обработки ошибок
- **Retry логика**: Экспоненциальный backoff для устойчивости (3 попытки)
- **Graceful degradation**: Fallback ответы при ошибках LLM
- **Graceful shutdown**: Корректное завершение по Ctrl+C через ApplicationContext
- **Структурированное логирование**: Цветной вывод и логи в файл (structlog)

### Качество кода
- **Строгая типизация**: Mypy strict mode, TypedDict, Literal, Protocol
- **DRY принцип**: Централизованные сообщения через Enum классы
- **High coverage**: 87.59% покрытие тестами (149 тестов)
- **Code quality**: Ruff (linter + formatter) + Mypy (type checker)
- **PEP 561**: Полная поддержка type hints (py.typed маркер)
- **Автоматизация**: make quality проверяет всё за один запуск

## 🧪 Тестирование

Проект имеет высокое покрытие тестами: **149 тестов, 87.59% coverage**

```bash
make test     # Запустить все 149 тестов
make quality  # Полная проверка (lint + types + tests)
```

**Типы тестов:**
- **Unit тесты**: Отдельные компоненты (Config, LLMClient, DialogManager, ConsoleApp, Logger)
- **Интеграционные тесты**: Все сценарии из vision.md
- **Тесты исключений**: Кастомная иерархия ошибок (LLMError, ConfigError)
- **Тесты retry логики**: Экспоненциальный backoff с различными сценариями
- **Тесты типизации**: TypedDict, Literal, Protocol
- **Тесты сообщений**: DRY принцип для Enum классов
- **Тесты ошибок**: Различные типы ошибок API (rate limit, timeout, 5xx, 4xx)
- **Параметризованные тесты**: Edge cases с разными значениями
- **Async тесты**: Все асинхронные операции покрыты

**Покрытие по модулям:**
- dialog_manager.py: 100%
- exceptions.py: 100%
- types.py: 100%
- messages.py: 100%
- logger.py: 100%
- console.py: 99%
- llm_client.py: 97%
- config.py: 94%
- retry_utils.py: 90%

## 🛡️ Обработка ошибок

Приложение использует иерархию кастомных исключений для точной обработки:

**Иерархия исключений:**
- `AppError` - базовое исключение приложения
  - `ConfigError` - ошибки конфигурации
  - `LLMError` - базовое исключение для LLM
    - `LLMRateLimitError` - превышен rate limit
    - `LLMConnectionError` - ошибка подключения
    - `LLMTimeoutError` - таймаут запроса
    - `LLMServerError` - серверная ошибка (5xx)
    - `LLMClientError` - клиентская ошибка (4xx)
    - `LLMEmptyResponseError` - пустой ответ
  - `RetryError` - исчерпаны попытки retry

**Механизмы обработки:**
- **Rate Limit**: Автоматические повторные попытки с экспоненциальным backoff (max 3)
- **Connection Error**: Повторные попытки подключения с задержкой
- **API Timeout**: Обработка таймаутов с fallback ответами
- **Server Errors (5xx)**: Retry логика для временных ошибок
- **Client Errors (4xx)**: Без retry, понятные сообщения пользователю
- **Configuration Error**: Валидация конфигурации при запуске (Pydantic)
- **Keyboard Interrupt**: Graceful shutdown через ApplicationContext

**Fallback механизм:**
- При ошибке LLM используются заранее подготовленные ответы
- 4 варианта fallback сообщений (выбор по длине запроса)
- Логирование всех ошибок для анализа

## 📄 Лицензия

MIT License