# Настройка базы данных PostgreSQL

## Быстрый старт

### 1. Запуск PostgreSQL в Docker

```bash
# Запуск PostgreSQL и pgAdmin
docker-compose up -d

# Проверка статуса
docker-compose ps
```

### 2. Применение миграций

```bash
# Применить все миграции
uv run alembic upgrade head

# Откатить миграцию
uv run alembic downgrade -1

# Посмотреть историю миграций
uv run alembic history
```

### 3. Проверка подключения

PostgreSQL будет доступен:
- **Host:** localhost
- **Port:** 5434
- **Database:** aidd_db
- **User:** aidd_user
- **Password:** aidd_password

pgAdmin (опционально):
- **URL:** http://localhost:5050
- **Email:** admin@aidd.local
- **Password:** admin

### 4. Настройка .env

Добавьте в файл `.env`:

```env
DATABASE_URL=postgresql://aidd_user:aidd_password@localhost:5434/aidd_db
DATABASE_POOL_MIN_SIZE=5
DATABASE_POOL_MAX_SIZE=20
```

## Структура БД

### Таблица messages

```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    role VARCHAR(20) NOT NULL,  -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,       -- Содержимое сообщения
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),  -- Время создания
    length INTEGER NOT NULL,     -- Длина сообщения в символах
    deleted_at TIMESTAMP NULL    -- Soft delete (NULL = активное)
);

CREATE INDEX idx_messages_deleted_at ON messages(deleted_at);
```

### Особенности

- **Soft delete:** Сообщения не удаляются физически, а помечаются через `deleted_at`
- **Автоматические метаданные:** `created_at` и `length` добавляются автоматически
- **Индексация:** Индекс на `deleted_at` для быстрой выборки активных сообщений

## Управление

### Остановка БД

```bash
docker-compose down
```

### Остановка с удалением данных

```bash
docker-compose down -v
```

### Просмотр логов

```bash
docker-compose logs -f postgres
```

## Миграции

### Создание новой миграции

```bash
uv run alembic revision -m "описание_изменений"
```

### Проверка текущей версии

```bash
uv run alembic current
```

## Устранение неполадок

### Ошибка подключения

1. Проверьте что контейнер запущен: `docker-compose ps`
2. Проверьте логи: `docker-compose logs postgres`
3. Проверьте DATABASE_URL в .env

### База данных не создается

Используйте команду для пересоздания:

```bash
docker-compose down -v
docker-compose up -d
sleep 10
uv run alembic upgrade head
```

