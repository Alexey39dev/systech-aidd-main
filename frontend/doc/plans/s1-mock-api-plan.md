# План реализации FS-001: Mock API для дашборда статистики

## 1. Анализ требований и проектирование контрактов

### 1.1 Документация функциональных требований

Создать `frontend/doc/dashboard-requirements.md` с функциональными требованиями к дашборду на основе референса https://ui.shadcn.com/blocks#dashboard-01:

- 4 метрика-блока: Total Dialogs, Active Users, Avg Dialog Length, Messages Today
- Timeline график активности сообщений по времени
- Список последних диалогов (Recent Dialogs) с user, messages count, last activity
- Топ активных пользователей (Top Users) с количеством сообщений

### 1.2 Проектирование API контракта

Создать `src/api/schemas.py` с Pydantic моделями для API:

```python
class StatsRequest:
    period: Literal["day", "week", "month"]

class MetricCard:
    label: str
    value: str | int
    change: str  # например "+12.5%"
    trend: Literal["up", "down", "neutral"]

class TimelinePoint:
    timestamp: str  # ISO format
    value: int

class RecentDialog:
    user_id: int
    username: str
    messages_count: int
    last_activity: str  # ISO format

class TopUser:
    user_id: int
    username: str
    messages_count: int
    dialogs_count: int

class StatsResponse:
    period: str
    metrics: list[MetricCard]  # 4 блока
    timeline: list[TimelinePoint]
    recent_dialogs: list[RecentDialog]
    top_users: list[TopUser]
```

**Пример JSON ответа для period=day:**

```json
{
  "period": "day",
  "metrics": [
    {
      "label": "Total Dialogs",
      "value": 1247,
      "change": "+12.5%",
      "trend": "up"
    },
    {
      "label": "Active Users",
      "value": 58,
      "change": "+5.2%",
      "trend": "up"
    },
    {
      "label": "Avg Dialog Length",
      "value": 8.3,
      "change": "-2.1%",
      "trend": "down"
    },
    {
      "label": "Messages Today",
      "value": 342,
      "change": "+18.7%",
      "trend": "up"
    }
  ],
  "timeline": [
    { "timestamp": "2025-10-17T00:00:00Z", "value": 12 },
    { "timestamp": "2025-10-17T01:00:00Z", "value": 8 },
    { "timestamp": "2025-10-17T02:00:00Z", "value": 5 },
    { "timestamp": "2025-10-17T03:00:00Z", "value": 3 },
    "... 24 точки (почасовая разбивка)"
  ],
  "recent_dialogs": [
    {
      "user_id": 42,
      "username": "alice_wonder",
      "messages_count": 15,
      "last_activity": "2025-10-17T14:23:15Z"
    },
    {
      "user_id": 17,
      "username": "bob_builder",
      "messages_count": 23,
      "last_activity": "2025-10-17T14:18:42Z"
    },
    "... до 10 последних диалогов"
  ],
  "top_users": [
    {
      "user_id": 7,
      "username": "power_user_123",
      "messages_count": 156,
      "dialogs_count": 12
    },
    {
      "user_id": 23,
      "username": "chat_master",
      "messages_count": 142,
      "dialogs_count": 18
    },
    "... топ 10 пользователей"
  ]
}
```

## 2. Реализация интерфейса и Mock сборщика статистики

### 2.1 Интерфейс StatCollector

Создать `src/api/stat_collector.py` с абстрактным базовым классом:

```python
from abc import ABC, abstractmethod

class StatCollector(ABC):
    @abstractmethod
    async def get_stats(self, period: str) -> StatsResponse:
        """Получить статистику за указанный период."""
        pass
```

### 2.2 Mock реализация

Создать `src/api/mock_stat_collector.py` с MockStatCollector:

- Генерация 50-70 тестовых пользователей с реалистичными username
- Генерация 1000-1500 сообщений с распределением по времени (последние 30 дней)
- Разнообразные роли (user/assistant/system) с правдоподобными пропорциями (40% user, 40% assistant, 20% system)
- Генерация данных при инициализации (метод `_generate_mock_data()`)
- Реализация `get_stats(period)` с гибкой детализацией timeline:
  - `day`: почасовая разбивка (24 точки)
  - `week`: ежедневная разбивка (7 точек)
  - `month`: ежедневная разбивка (30 точек)
- Расчет метрик, топов, последних диалогов на основе сгенерированных данных

**Формат внутренних тестовых данных:**

```python
self._users: list[dict] = [
    {"id": 1, "username": "alice_wonder", "created_at": datetime(...)},
    {"id": 2, "username": "bob_builder", "created_at": datetime(...)},
]
self._messages: list[dict] = [
    {"id": 1, "user_id": 1, "role": "user", "content": "...", "length": 27, "created_at": datetime(...)},
    {"id": 2, "user_id": 1, "role": "assistant", "content": "...", "length": 45, "created_at": datetime(...)},
]
```

## 3. FastAPI Application

### 3.1 Основной файл API

Создать `src/api/app.py` с FastAPI приложением:

- Инициализация FastAPI с заголовком, описанием, версией
- Настройка автогенерации OpenAPI документации
- Dependency для получения StatCollector
- Endpoint `GET /api/stats` с параметром `period` (query param с валидацией)
- Обработка ошибок и возврат корректных HTTP статусов

### 3.2 Entrypoint для запуска

Создать `src/api/main.py`:

- Конфигурация uvicorn
- Запуск API сервера на порту 8000
- Поддержка reload в dev режиме

### 3.3 Конфигурация API

Расширить `src/config.py`:

- Добавить параметры `api_host` (default: "0.0.0.0")
- Добавить параметры `api_port` (default: 8000)
- Добавить параметры `api_reload` (default: True)
- Добавить параметры `stat_collector_type` (default: "mock", варианты: "mock" | "real")

## 4. Зависимости и инфраструктура

### 4.1 Обновление зависимостей

Добавить в `pyproject.toml`:

```toml
dependencies = [
    ...
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
]
```

### 4.2 Создание директорий

- `src/api/` - модуль API
- `src/api/__init__.py` - экспорт основных компонентов

## 5. Команды и автоматизация

### 5.1 Обновление Makefile

Добавить новые команды:

```makefile
run-api:
    @echo "Запуск Mock API сервера..."
    uv run python -m src.api.main

test-api:
    @echo "Тестирование API..."
    @curl -X GET "http://localhost:8000/api/stats?period=day" | python -m json.tool
    @curl -X GET "http://localhost:8000/api/stats?period=week" | python -m json.tool
    @curl -X GET "http://localhost:8000/api/stats?period=month" | python -m json.tool

api-docs:
    @echo "Открытие документации API..."
    @start http://localhost:8000/docs
```

## 6. Документация и примеры

### 6.1 Документация API

Создать `frontend/doc/api-specification.md`:

- Описание endpoint `/api/stats`
- Параметры запроса
- Примеры ответов для всех периодов (day/week/month)
- Описание моделей данных
- Примеры использования curl/httpie

### 6.2 README для API

Создать `src/api/README.md`:

- Быстрый старт
- Как запустить API
- Как протестировать
- Ссылка на полную спецификацию

## 7. Тестирование

### 7.1 Unit тесты

Создать `tests/test_mock_stat_collector.py`:

- Тест генерации mock данных
- Тест корректности статистики для разных периодов
- Тест детализации timeline
- Тест валидации данных

### 7.2 Integration тесты API

Создать `tests/test_api.py`:

- Тест GET /api/stats с разными периодами
- Тест валидации параметров
- Тест OpenAPI схемы
- Тест обработки ошибок

## Результат спринта

После выполнения плана будет:

- ✅ Функциональные требования к дашборду
- ✅ Спроектированный API контракт с Pydantic моделями
- ✅ Интерфейс StatCollector и Mock реализация
- ✅ Работающий FastAPI сервер с документацией
- ✅ Реалистичные тестовые данные (50+ пользователей, 1000+ сообщений)
- ✅ Команды запуска и тестирования в Makefile
- ✅ Unit и integration тесты
- ✅ Полная документация API

## Список задач (TODO)

- [ ] Создать документацию функциональных требований к дашборду (frontend/doc/dashboard-requirements.md)
- [ ] Спроектировать и реализовать Pydantic модели для API контракта (src/api/schemas.py)
- [ ] Создать абстрактный интерфейс StatCollector (src/api/stat_collector.py)
- [ ] Реализовать MockStatCollector с генерацией реалистичных данных (src/api/mock_stat_collector.py)
- [ ] Создать FastAPI приложение с endpoint /api/stats (src/api/app.py)
- [ ] Создать entrypoint для запуска API сервера (src/api/main.py)
- [ ] Расширить Config для API параметров (src/config.py)
- [ ] Добавить FastAPI и uvicorn в зависимости (pyproject.toml)
- [ ] Добавить команды run-api, test-api, api-docs в Makefile
- [ ] Создать полную документацию API спецификации (frontend/doc/api-specification.md)
- [ ] Создать README для API модуля (src/api/README.md)
- [ ] Написать unit тесты для MockStatCollector (tests/test_mock_stat_collector.py)
- [ ] Написать integration тесты для API (tests/test_api.py)
- [ ] Создать примеры запросов к API для тестирования (curl/httpie команды)
- [ ] Добавить ссылку на план реализации в таблицу спринтов в doc/frontend-roadmap.md
- [ ] Актуализировать статус спринта FS-001 в doc/frontend-roadmap.md после завершения
