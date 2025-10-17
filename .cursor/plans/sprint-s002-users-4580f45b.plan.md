<!-- 4580f45b-5052-45e9-9d8d-0e116b85e666 8a181ebb-c904-4af1-a768-d36cdd76d180 -->
# Sprint S002: Управление пользователями

## Обзор

Реализация персистентного хранения информации о пользователях (username) в базе данных. При запуске приложения пользователь вводит свое имя, которое сохраняется в БД. Все сообщения привязываются к пользователю через внешний ключ.

## Архитектурные решения (KISS)

- **Таблица users**: id, username, created_at, updated_at, deleted_at
- **Внешний ключ**: user_id в таблице messages
- **get_or_create_user**: если username существует - обновить updated_at и вернуть id, иначе создать нового
- **Username**: запрашивается один раз при старте приложения через input()
- **Миграции**: две последовательные миграции Alembic с raw SQL
- **Soft delete**: поддержка deleted_at для users

## Ключевые файлы

### Новые файлы

- `alembic/versions/[hash]_create_users_table.py` - создание таблицы users
- `alembic/versions/[hash]_add_user_id_to_messages.py` - добавление user_id в messages

### Изменяемые файлы

- `src/types.py` - добавить UserDBDict TypedDict
- `src/database.py` - методы get_or_create_user(), soft_delete_user()
- `src/dialog_manager.py` - конструктор принимает user_id, передает в add_message
- `src/console.py` - конструктор принимает user_id
- `src/main.py` - запрос username при старте, получение user_id
- `tests/test_database.py` - тесты для users
- `tests/test_dialog_manager.py` - обновить моки для user_id
- `tests/test_console.py` - обновить моки для user_id
- `tests/test_integration.py` - обновить интеграционные тесты

## План реализации

### 1. Схема БД и миграции

```sql
-- Миграция 1: create_users_table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP NULL
);
CREATE INDEX idx_users_username ON users(username) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_deleted_at ON users(deleted_at);

-- Миграция 2: add_user_id_to_messages
ALTER TABLE messages ADD COLUMN user_id INTEGER;
ALTER TABLE messages ADD CONSTRAINT fk_messages_user_id 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;
CREATE INDEX idx_messages_user_id ON messages(user_id);
```

### 2. Типы данных (src/types.py)

```python
class UserDBDict(TypedDict):
    id: int
    username: str
    created_at: str
    updated_at: str
    deleted_at: str | None
```

### 3. DatabaseClient методы

```python
async def get_or_create_user(self, username: str) -> tuple[int, datetime]:
    # Ищем активного пользователя с таким username
    # Если найден - обновляем updated_at, возвращаем id
    # Если не найден - создаем нового, возвращаем id
    
async def soft_delete_user(self, user_id: int) -> None:
    # SET deleted_at = NOW() WHERE id = user_id
```

### 4. DialogManager изменения

```python
def __init__(self, db_client: DatabaseClient, user_id: int, max_history: int = 10):
    self.user_id = user_id
    # ...

async def add_message(self, role: MessageRole, content: str) -> None:
    message_id, created_at = await self.db_client.add_message(
        role, content, self.user_id
    )
```

### 5. ConsoleApp изменения

```python
def __init__(self, config: Config, db_client: DatabaseClient, user_id: int):
    self.dialog_manager = DialogManager(
        db_client=db_client, user_id=user_id, max_history=config.max_history
    )
```

### 6. main.py - запрос username

```python
async def main() -> int:
    # ... после db_client.connect()
    
    # Запрос username у пользователя
    username = input("Введите ваше имя: ").strip()
    if not username:
        username = "anonymous"
    
    user_id, _ = await db_client.get_or_create_user(username)
    logger.info("Пользователь инициализирован", user_id=user_id, username=username)
    
    # Создание консольного приложения с user_id
    app = ConsoleApp(config, db_client, user_id)
```

## Тестирование

- Unit тесты для DatabaseClient.get_or_create_user()
- Unit тесты для DatabaseClient.soft_delete_user()
- Обновить существующие тесты с моками user_id
- Интеграционные тесты для полного флоу с users
- Coverage должен остаться >80%

## Критерии завершения

- ✅ Миграции применяются без ошибок
- ✅ Username сохраняется в БД при первом запуске
- ✅ Username обновляет updated_at при повторном запуске
- ✅ Все сообщения привязаны к user_id
- ✅ Все тесты проходят (pytest)
- ✅ Coverage >= 87%
- ✅ Mypy strict mode без ошибок
- ✅ Ruff без ошибок

### To-dos

- [ ] Создать миграцию Alembic для таблицы users (id, username, created_at, updated_at, deleted_at)
- [ ] Создать миграцию для добавления user_id в messages с внешним ключом
- [ ] Добавить UserDBDict в src/types.py
- [ ] Добавить методы get_or_create_user() и soft_delete_user() в DatabaseClient
- [ ] Обновить DatabaseClient.add_message() для работы с user_id
- [ ] Обновить DialogManager для передачи user_id в add_message
- [ ] Обновить ConsoleApp для приема user_id в конструкторе
- [ ] Добавить запрос username и получение user_id в main.py
- [ ] Написать тесты для методов users в DatabaseClient
- [ ] Обновить существующие тесты для работы с user_id
- [ ] Запустить make quality и исправить все ошибки