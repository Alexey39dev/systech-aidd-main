# План спринта D0: Basic Docker Setup

## Цель

Запустить все сервисы локально через docker-compose одной командой. Создать простые Dockerfile для каждого сервиса без преждевременной оптимизации.

## Архитектура сервисов

Проект состоит из 4 сервисов:

1. **PostgreSQL** (уже есть в docker-compose.yml) - база данных
2. **Bot** (консольное приложение `src/main.py`) - Python приложение с UV
3. **API** (FastAPI сервис `src/api/app.py`) - Python приложение с UV  
4. **Frontend** (Next.js `frontend/`) - Node.js приложение с pnpm

## Конфигурация

Все переменные окружения определены в `src/config.py` через Pydantic с дефолтными значениями:

- База данных: `postgresql://aidd_user:aidd_password@postgres:5432/aidd_db` (внутри Docker)
- API порт: 8000
- Frontend порт: 3000
- OpenRouter API Key: требуется для работы LLM

**Важно**: В DATABASE_URL hostname должен быть `postgres` (имя сервиса), порт `5432` (внутренний порт контейнера).

## Этапы реализации

### 1. Создать .env.example файл

Создать шаблон переменных окружения на основе `src/config.py`:

```env
# OpenRouter API Configuration
OPENROUTER_API_KEY=your_key_here

# LLM Configuration  
SYSTEM_PROMPT=Ты полезный ассистент...
MAX_HISTORY=10
LLM_MODEL=openai/gpt-3.5-turbo
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1000

# Database Configuration (для Docker)
DATABASE_URL=postgresql://aidd_user:aidd_password@postgres:5432/aidd_db
DATABASE_POOL_MIN_SIZE=5
DATABASE_POOL_MAX_SIZE=20

# Logging
LOG_LEVEL=INFO
LOG_TO_FILE=false
LOG_COLORFUL=true

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false
STAT_COLLECTOR_TYPE=mock

# Chat Configuration
CHAT_ENABLED=true
TEXT_TO_SQL_ENABLED=true
SESSION_EXPIRE_HOURS=24
```

### 2. Создать Dockerfile.bot

Простой single-stage Dockerfile для консольного приложения:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установка UV
RUN pip install uv

# Копирование файлов проекта
COPY pyproject.toml .
COPY src/ ./src/
COPY prompts/ ./prompts/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Установка зависимостей через UV
RUN uv pip install --system -e .

# Запуск бота
CMD ["python", "-m", "src.main"]
```

**Размер**: ~15 строк, простой и понятный.

### 3. Создать Dockerfile.api

Простой single-stage Dockerfile для FastAPI:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установка UV
RUN pip install uv

# Копирование файлов проекта
COPY pyproject.toml .
COPY src/ ./src/
COPY prompts/ ./prompts/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Установка зависимостей через UV
RUN uv pip install --system -e .

# Открытие порта
EXPOSE 8000

# Запуск API через uvicorn
CMD ["python", "-m", "uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Размер**: ~18 строк, без reload для стабильности в контейнере.

### 4. Создать Dockerfile.frontend

Простой single-stage Dockerfile для Next.js (dev режим для MVP):

```dockerfile
FROM node:20-alpine

WORKDIR /app

# Установка pnpm
RUN npm install -g pnpm

# Копирование package.json и pnpm-lock.yaml
COPY frontend/package.json frontend/pnpm-lock.yaml ./

# Установка зависимостей
RUN pnpm install

# Копирование остальных файлов
COPY frontend/ .

# Открытие порта
EXPOSE 3000

# Запуск в dev режиме (для MVP)
CMD ["pnpm", "dev"]
```

**Размер**: ~15 строк, простой dev режим.

### 5. Создать .dockerignore файлы

#### .dockerignore (для Bot и API - Python сервисы)

```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
.pytest_cache/
.mypy_cache/
.ruff_cache/
htmlcov/
.coverage
*.log
logs/
.env
.venv/
venv/
.git/
.gitignore
*.md
docs/
tests/
frontend/
node_modules/
.next/
```

#### frontend/.dockerignore (для Frontend)

```
node_modules/
.next/
.git/
.gitignore
*.md
__pycache__/
*.pyc
.pytest_cache/
htmlcov/
logs/
.env
dist/
build/
out/
.DS_Store
Thumbs.db
```

### 6. Обновить docker-compose.yml

Расширить существующий `docker-compose.yml` (где уже есть postgres и pgadmin):

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: systech-aidd-postgres
    environment:
      POSTGRES_USER: aidd_user
      POSTGRES_PASSWORD: aidd_password
      POSTGRES_DB: aidd_db
    ports:
      - "5434:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U aidd_user -d aidd_db"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - systech-network

  # Сервис миграций БД (один раз при старте)
  migrations:
    build:
      context: .
      dockerfile: Dockerfile.api
    container_name: systech-aidd-migrations
    env_file:
      - .env
    depends_on:
      postgres:
        condition: service_healthy
    command: ["python", "-m", "alembic", "upgrade", "head"]
    networks:
      - systech-network

  bot:
    build:
      context: .
      dockerfile: Dockerfile.bot
    container_name: systech-aidd-bot
    env_file:
      - .env
    depends_on:
      postgres:
        condition: service_healthy
      migrations:
        condition: service_completed_successfully
    restart: unless-stopped
    networks:
      - systech-network

  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    container_name: systech-aidd-api
    env_file:
      - .env
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      migrations:
        condition: service_completed_successfully
    restart: unless-stopped
    networks:
      - systech-network

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    container_name: systech-aidd-frontend
    ports:
      - "3000:3000"
    depends_on:
      - api
    environment:
      - NEXT_PUBLIC_API_URL=http://api:8000
    restart: unless-stopped
    networks:
      - systech-network

  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: systech-aidd-pgadmin
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@aidd.local
      PGADMIN_DEFAULT_PASSWORD: admin
    ports:
      - "5050:80"
    depends_on:
      - postgres
    restart: unless-stopped
    profiles:
      - tools
    networks:
      - systech-network

volumes:
  postgres_data:
    driver: local

networks:
  systech-network:
    driver: bridge
```

**Ключевые моменты**:

- Добавлен сервис `migrations` для автоматического запуска миграций при старте
- Все сервисы используют `depends_on` с `condition` для правильной последовательности запуска
- Единая сеть `systech-network` для всех сервисов
- `env_file: .env` для загрузки переменных окружения

### 7. Обновить README.md

Добавить секцию с Docker инструкциями:

````markdown
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
````

### 8. Создать devops/doc/plans/d0-basic-docker-setup.md

Сохранить этот план в файл для документации.

### 9. Обновить devops-roadmap.md

После завершения спринта обновить статус и добавить ссылку на план в таблице спринтов:

**В таблице спринтов:**

```markdown
| Код | Описание | Статус |
|-----|----------|--------|
| D0 | Basic Docker Setup | ✅ Завершен |
```

**В секции спринта D0:**

```markdown
## D0: Basic Docker Setup

**План реализации:** [d0-basic-docker-setup.md](plans/d0-basic-docker-setup.md)
```

## Проверка работоспособности

После выполнения всех этапов:

1. Скопировать `.env.example` в `.env` и добавить `OPENROUTER_API_KEY`
2. Запустить `docker-compose up`
3. Проверить логи всех сервисов
4. Открыть http://localhost:8000/docs - API должно быть доступно
5. Открыть http://localhost:3000/dashboard - Frontend должен загрузиться
6. Проверить логи бота - должно быть ожидание ввода от пользователя

## Ожидаемый результат

- ✅ Все 4 сервиса запускаются одной командой `docker-compose up`
- ✅ PostgreSQL стартует с healthcheck
- ✅ Миграции применяются автоматически
- ✅ Bot, API и Frontend подключаются к PostgreSQL
- ✅ Frontend может делать запросы к API
- ✅ Простые и понятные Dockerfile (~15-20 строк)
- ✅ Базовые .dockerignore файлы исключают ненужные файлы
- ✅ README обновлен с инструкциями по Docker

## Примечания

- **MVP подход**: Используем dev режим для Next.js (простота важнее оптимизации)
- **Без multi-stage**: Single-stage Dockerfile для простоты
- **Без оптимизации размера**: Фокус на работоспособности
- **Миграции автоматически**: Через отдельный init-контейнер
- **Все в одной сети**: Простая конфигурация сети Docker

## Список задач (To-do)

- [ ] Подготовка конфигурации: создать .env.example с шаблоном всех переменных окружения
- [ ] Создать простой Dockerfile.bot (single-stage, Python + UV, ~15 строк)
- [ ] Создать простой Dockerfile.api (single-stage, Python + UV, ~18 строк)
- [ ] Создать простой Dockerfile.frontend (single-stage, Node + pnpm, ~15 строк)
- [ ] Создать .dockerignore для Python сервисов - исключить __pycache__, .git, logs
- [ ] Создать frontend/.dockerignore - исключить node_modules, .next, .git
- [ ] Создать docker-compose.yml с 4 сервисами (postgres, bot, api, frontend, migrations)
- [ ] Настроить сеть systech-network и depends_on с условиями запуска
- [ ] Локальное тестирование: docker-compose up и проверка работы всех сервисов
- [ ] Проверить доступность API (http://localhost:8000/docs)
- [ ] Проверить доступность Frontend (http://localhost:3000/dashboard)
- [ ] Обновление README.md с инструкциями по запуску через Docker
- [ ] Сохранить план в devops/doc/plans/d0-basic-docker-setup.md
- [ ] Актуализация devops-roadmap.md: изменить статус D0 на ✅ Завершен
- [ ] Добавить ссылку на план реализации в таблицу и секцию спринта D0

