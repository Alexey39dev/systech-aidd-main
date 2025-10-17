<!-- 22a47090-84e1-4f26-8512-12194be28ce8 dfff0104-7061-41d7-88e4-4ded34c33089 -->
# План реализации Sprint S001: Персистентное хранение данных

## Цель

Перейти от in-memory хранения к персистентному хранению истории диалогов в PostgreSQL с использованием raw SQL (asyncpg), системой миграций Alembic, soft delete стратегией и метаданными сообщений.

## Ключевые решения

**СУБД:** PostgreSQL в Docker

**Библиотека:** asyncpg (raw SQL) + Alembic (миграции)

**Стратегия:** Soft delete только для сообщений

**Новые поля:** `created_at` (timestamp), `length` (int), `deleted_at` (nullable timestamp)

## Основные изменения

### 1. Инфраструктура (Docker)

Создать `docker-compose.yml` с PostgreSQL и pgAdmin:

- PostgreSQL 16 (порт 5432)
- pgAdmin 4 для управления (опционально)
- Volume для персистентности данных
- База данных создается автоматически при старте

### 2. Настройка миграций (Alembic)

Инициализировать Alembic для работы без ORM:

- `alembic init alembic` - создать структуру
- Настроить `alembic.ini` (database URL)
- Настроить `alembic/env.py` для raw SQL режима
- Создать первую миграцию с DDL командами:
```python
def upgrade():
    op.execute("""
        CREATE TABLE messages (
            id SERIAL PRIMARY KEY,
            role VARCHAR(20) NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            length INTEGER NOT NULL,
            deleted_at TIMESTAMP NULL
        );
        CREATE INDEX idx_messages_deleted_at ON messages(deleted_at);
    """)

def downgrade():
    op.execute("DROP TABLE IF EXISTS messages;")
```


### 3. Конфигурация БД

Расширить `src/config.py`:

- `database_url` (строка подключения PostgreSQL)
- `database_pool_min_size` (default=5)
- `database_pool_max_size` (default=20)

### 4. Типизация

Обновить `src/types.py`:

```python
class MessageDict(TypedDict):
    role: MessageRole
    content: str
    created_at: str  # ISO format
    length: int

class MessageDBDict(TypedDict):
    id: int
    role: MessageRole
    content: str
    created_at: str
    length: int
    deleted_at: str | None
```

### 5. Слой доступа к данным

Создать `src/database.py` с классом `DatabaseClient`:

- `async def connect()` - создание пула asyncpg
- `async def close()` - закрытие пула
- `async def add_message(role, content)` - INSERT через raw SQL
  ```sql
  INSERT INTO messages (role, content, length) 
  VALUES ($1, $2, $3) 
  RETURNING id, created_at
  ```

- `async def get_messages()` - SELECT активных сообщений
  ```sql
  SELECT id, role, content, created_at, length, deleted_at 
  FROM messages 
  WHERE deleted_at IS NULL 
  ORDER BY created_at ASC
  ```

- `async def soft_delete_message(message_id)` - UPDATE deleted_at
  ```sql
  UPDATE messages SET deleted_at = NOW() WHERE id = $1
  ```

- `async def clear_all_messages()` - UPDATE deleted_at для всех
  ```sql
  UPDATE messages SET deleted_at = NOW() WHERE deleted_at IS NULL
  ```


### 6. Рефакторинг DialogManager

Обновить `src/dialog_manager.py`:

- Добавить зависимость от `DatabaseClient`
- Изменить `add_message()` - сохранять в БД с автоматическим подсчетом length
- Изменить `get_history()` - загружать из БД, конвертировать в MessageDict
- Изменить `clear_history()` - вызывать `db.clear_all_messages()`
- Удалить `self.history: list[Message]` (in-memory хранение)
- Обновить `_trim_history()` - вызывать soft_delete для старых записей

### 7. Обновление main.py

- Инициализировать `DatabaseClient` при старте
- Передать `db_client` в `DialogManager`
- Закрывать соединение при shutdown

### 8. Тестирование

Создать `tests/test_database.py`:

- Unit тесты для `DatabaseClient` (с моками asyncpg.Pool)
- Тесты CRUD операций
- Тесты soft delete
- Тесты метаданных (created_at, length)
- Проверка SQL инъекций (параметризованные запросы)

Обновить `tests/test_dialog_manager.py`:

- Добавить фикстуру с mock `DatabaseClient`
- Адаптировать существующие тесты (моки возвращают MessageDBDict)

Создать `tests/test_integration_db.py`:

- Интеграционные тесты с реальной PostgreSQL
- Использовать test БД или Docker контейнер для тестов
- Тесты полного flow: добавление → получение → soft delete → миграции

## Порядок реализации (TDD)

1. **Инфраструктура**: docker-compose.yml
2. **Конфигурация**: расширить Config с DB параметрами
3. **Миграции**: настроить Alembic, создать миграцию с CREATE TABLE
4. **Типы**: обновить types.py (MessageDict, MessageDBDict)
5. **Database Client** (TDD):

   - RED: тесты для connect/close с asyncpg.Pool
   - GREEN: реализация пула соединений
   - RED: тесты для add_message с метаданными
   - GREEN: реализация INSERT с параметрами
   - RED: тесты для get_messages (только не удаленные)
   - GREEN: реализация SELECT с WHERE
   - RED: тесты для soft_delete
   - GREEN: реализация UPDATE deleted_at

6. **DialogManager рефакторинг** (TDD):

   - RED: обновить тесты под новый API с DB
   - GREEN: интегрировать DatabaseClient
   - REFACTOR: убрать in-memory хранение

7. **Integration**: обновить main.py, добавить lifecycle управление
8. **Testing**: интеграционные тесты с реальной БД

## Зависимости (добавить в pyproject.toml)

```toml
[project.dependencies]
asyncpg = ">=0.29.0"
alembic = ">=1.13.0"
```

## Критерии готовности

- ✅ PostgreSQL работает в Docker
- ✅ Alembic настроен и миграции работают (raw SQL mode)
- ✅ Таблица messages создана через миграцию
- ✅ DatabaseClient реализован с raw SQL запросами
- ✅ Все SQL запросы параметризованы (защита от инъекций)
- ✅ DialogManager использует БД вместо памяти
- ✅ Soft delete работает корректно
- ✅ Метаданные created_at и length сохраняются автоматически
- ✅ Все существующие тесты адаптированы и проходят
- ✅ Coverage >80%
- ✅ make quality проходит без ошибок

### To-dos

- [ ] Создать docker-compose.yml с PostgreSQL и init schema
- [ ] Расширить Config с параметрами БД
- [ ] Обновить типы Message и добавить MessageDB
- [ ] Реализовать DatabaseClient (TDD: connect, add_message, get_messages, soft_delete)
- [ ] Рефакторинг DialogManager для использования DatabaseClient
- [ ] Обновить main.py для lifecycle управления БД
- [ ] Создать интеграционные тесты с реальной PostgreSQL
- [ ] Финальная проверка: make quality, coverage >80%