# API Specification: Dialog Statistics API

## Обзор

Dialog Statistics API предоставляет endpoint для получения статистики диалогов пользователей с AI-ассистентом. API построено на FastAPI и предоставляет автоматическую OpenAPI документацию.

**Base URL**: `http://localhost:8000`

**Документация**:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI Schema: http://localhost:8000/openapi.json

## Endpoints

### GET /

Информационный endpoint с метаданными API.

**Response:**

```json
{
  "name": "Dialog Statistics API",
  "version": "1.0.0",
  "docs": "/docs",
  "endpoints": {
    "stats": "/api/stats?period={day|week|month}"
  }
}
```

### GET /api/stats

Получить статистику диалогов за указанный период.

**Query Parameters:**

| Parameter | Type   | Required | Default | Description                               |
| --------- | ------ | -------- | ------- | ----------------------------------------- |
| period    | string | No       | "day"   | Период статистики: "day", "week", "month" |

**Request Examples:**

```bash
# Статистика за день
curl -X GET "http://localhost:8000/api/stats?period=day"

# Статистика за неделю
curl -X GET "http://localhost:8000/api/stats?period=week"

# Статистика за месяц
curl -X GET "http://localhost:8000/api/stats?period=month"
```

**Response:** `StatsResponse`

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
    {
      "timestamp": "2025-10-17T00:00:00Z",
      "value": 12
    },
    {
      "timestamp": "2025-10-17T01:00:00Z",
      "value": 8
    },
    ...
  ],
  "recent_dialogs": [
    {
      "user_id": 42,
      "username": "alice_wonder",
      "messages_count": 15,
      "last_activity": "2025-10-17T14:23:15Z"
    },
    ...
  ],
  "top_users": [
    {
      "user_id": 7,
      "username": "power_user_123",
      "messages_count": 156,
      "dialogs_count": 12
    },
    ...
  ]
}
```

**Response Codes:**

| Code | Description                                |
| ---- | ------------------------------------------ |
| 200  | Success - статистика возвращена            |
| 400  | Bad Request - некорректный параметр period |
| 500  | Internal Server Error - ошибка сервера     |

**Error Response Example:**

```json
{
  "detail": "Invalid period: invalid. Must be 'day', 'week', or 'month'"
}
```

### GET /health

Health check endpoint для мониторинга работоспособности сервиса.

**Response:**

```json
{
  "status": "healthy",
  "collector_type": "mock"
}
```

## Data Models

### StatsResponse

Основная модель ответа со статистикой.

| Field          | Type                 | Description                                |
| -------------- | -------------------- | ------------------------------------------ |
| period         | string               | Период статистики ("day", "week", "month") |
| metrics        | array[MetricCard]    | Массив из 4 метрик-карточек                |
| timeline       | array[TimelinePoint] | Данные для графика активности              |
| recent_dialogs | array[RecentDialog]  | Последние диалоги (до 10)                  |
| top_users      | array[TopUser]       | Топ пользователей (до 10)                  |

### MetricCard

Карточка с метрикой для дашборда.

| Field  | Type                        | Description                                |
| ------ | --------------------------- | ------------------------------------------ |
| label  | string                      | Название метрики                           |
| value  | string \| int \| float      | Значение метрики                           |
| change | string                      | Изменение в процентах (например, "+12.5%") |
| trend  | "up" \| "down" \| "neutral" | Направление тренда                         |

### TimelinePoint

Точка данных для графика активности.

| Field     | Type    | Description                   |
| --------- | ------- | ----------------------------- |
| timestamp | string  | Временная метка в ISO формате |
| value     | integer | Количество сообщений (≥ 0)    |

**Timeline детализация по периодам:**

- **day**: 24 точки (почасовая разбивка)
- **week**: 7 точек (ежедневная разбивка)
- **month**: 30 точек (ежедневная разбивка)

### RecentDialog

Информация о недавнем диалоге.

| Field          | Type    | Description                             |
| -------------- | ------- | --------------------------------------- |
| user_id        | integer | ID пользователя (> 0)                   |
| username       | string  | Имя пользователя                        |
| messages_count | integer | Количество сообщений в диалоге (≥ 0)    |
| last_activity  | string  | Время последней активности (ISO формат) |

### TopUser

Информация о топ пользователе.

| Field          | Type    | Description                      |
| -------------- | ------- | -------------------------------- |
| user_id        | integer | ID пользователя (> 0)            |
| username       | string  | Имя пользователя                 |
| messages_count | integer | Общее количество сообщений (≥ 0) |
| dialogs_count  | integer | Количество диалогов (≥ 0)        |

## Примеры использования

### cURL

```bash
# Получить статистику за день
curl -X GET "http://localhost:8000/api/stats?period=day" \
  -H "Accept: application/json"

# Получить статистику за неделю с форматированием
curl -X GET "http://localhost:8000/api/stats?period=week" | python -m json.tool

# Health check
curl -X GET "http://localhost:8000/health"
```

### Python (requests)

```python
import requests

# Получение статистики
response = requests.get("http://localhost:8000/api/stats", params={"period": "day"})
stats = response.json()

print(f"Active Users: {stats['metrics'][1]['value']}")
print(f"Timeline points: {len(stats['timeline'])}")
```

### JavaScript (fetch)

```javascript
// Получение статистики за неделю
fetch("http://localhost:8000/api/stats?period=week")
  .then((response) => response.json())
  .then((data) => {
    console.log("Metrics:", data.metrics);
    console.log("Timeline:", data.timeline);
  });
```

### HTTPie

```bash
# Установка: pip install httpie

# Получить статистику
http GET http://localhost:8000/api/stats period==day

# С фильтрацией результата
http GET http://localhost:8000/api/stats period==month | jq '.metrics'
```

## CORS

API настроено с CORS middleware для работы с фронтендом:

- **allow_origins**: `["*"]` (в production указать конкретные домены)
- **allow_methods**: Все методы
- **allow_headers**: Все заголовки
- **allow_credentials**: True

## Версионирование

Текущая версия API: **v1.0.0**

API следует semantic versioning. Изменения:

- **Major** версия: Breaking changes (несовместимые изменения)
- **Minor** версия: Новый функционал (обратно совместимый)
- **Patch** версия: Исправления ошибок

## Ограничения

- Максимум 10 последних диалогов в `recent_dialogs`
- Максимум 10 пользователей в `top_users`
- Фиксированные периоды: day, week, month (без кастомных диапазонов)

## Аутентификация

В текущей версии (MVP) аутентификация **не требуется**. В будущих версиях планируется добавление:

- API Key authentication
- JWT tokens
- Rate limiting

## Rate Limiting

В текущей версии (MVP) rate limiting **отсутствует**. В production окружении рекомендуется настроить:

- Лимит запросов: 100 запросов/минуту на IP
- Burst: 10 запросов

## Мониторинг

Доступные endpoints для мониторинга:

- **Health Check**: `GET /health` - проверка работоспособности
- **Metrics**: (планируется) `GET /metrics` - Prometheus метрики

## Разработка

### Запуск локально

```bash
# Установка зависимостей
make install

# Запуск API сервера
make run-api

# Тестирование endpoints
make test-api

# Открытие документации
make api-docs
```

### Конфигурация

Параметры API настраиваются через `.env` файл:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true
STAT_COLLECTOR_TYPE=mock
```

## Поддержка

При возникновении вопросов или проблем:

1. Проверьте документацию: http://localhost:8000/docs
2. Проверьте health check: http://localhost:8000/health
3. Изучите логи сервера
