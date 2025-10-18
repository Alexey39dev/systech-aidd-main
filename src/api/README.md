# Dialog Statistics API

Mock API для получения статистики диалогов с AI-ассистентом. Предоставляет тестовые данные для разработки frontend дашборда.

## Быстрый старт

### 1. Установка зависимостей

```bash
make install
```

### 2. Запуск API сервера

```bash
make run-api
```

API будет доступно по адресу: **http://localhost:8000**

### 3. Открытие документации

```bash
make api-docs
```

Или перейдите в браузере: http://localhost:8000/docs

## Основные возможности

- ✅ **Mock данные**: 50-70 тестовых пользователей, 1000-1500 сообщений
- ✅ **Статистика за периоды**: day, week, month
- ✅ **Timeline графики**: Почасовая/ежедневная детализация
- ✅ **Топ пользователей**: Рейтинг по активности
- ✅ **Последние диалоги**: До 10 последних активных диалогов
- ✅ **OpenAPI документация**: Автоматическая генерация Swagger UI
- ✅ **CORS**: Настроен для работы с фронтендом

## Использование

### Получение статистики

```bash
# Статистика за день (по умолчанию)
curl http://localhost:8000/api/stats

# Статистика за неделю
curl http://localhost:8000/api/stats?period=week

# Статистика за месяц
curl http://localhost:8000/api/stats?period=month
```

### Тестирование API

```bash
# Запустить все тесты endpoints
make test-api
```

### Health Check

```bash
curl http://localhost:8000/health
```

## Структура ответа

API возвращает JSON со следующей структурой:

```json
{
  "period": "day",
  "metrics": [
    // 4 метрики-карточки
  ],
  "timeline": [
    // Данные для графика активности
  ],
  "recent_dialogs": [
    // До 10 последних диалогов
  ],
  "top_users": [
    // Топ 10 пользователей
  ]
}
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Информация об API |
| GET | `/api/stats` | Получить статистику |
| GET | `/health` | Health check |
| GET | `/docs` | Swagger UI документация |
| GET | `/redoc` | ReDoc документация |

## Конфигурация

Параметры настраиваются через файл `.env`:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true
STAT_COLLECTOR_TYPE=mock
```

## Архитектура

```
src/api/
├── __init__.py          # Экспорт основных компонентов
├── app.py               # FastAPI приложение
├── main.py              # Entrypoint для запуска
├── schemas.py           # Pydantic модели
├── stat_collector.py    # Абстрактный интерфейс
└── mock_stat_collector.py  # Mock реализация
```

### StatCollector Interface

Абстрактный интерфейс позволяет легко переключаться между Mock и Real реализациями:

```python
class StatCollector(ABC):
    @abstractmethod
    async def get_stats(self, period: str) -> StatsResponse:
        pass
```

### Mock Data Generation

MockStatCollector генерирует реалистичные данные:

- **Пользователи**: 50-70 пользователей с уникальными username
- **Сообщения**: 1000-1500 сообщений за последние 30 дней
- **Роли**: 40% user, 40% assistant, 20% system
- **Распределение**: Реалистичное распределение по времени суток

## Разработка

### Запуск в dev режиме

```bash
# С автоматической перезагрузкой при изменениях
API_RELOAD=true make run-api
```

### Структура данных

Mock данные хранятся в памяти:

```python
self._users: list[dict] = [
    {"id": 1, "username": "alice_wonder", "created_at": datetime(...)},
    ...
]

self._messages: list[dict] = [
    {"id": 1, "user_id": 1, "role": "user", "content": "...", ...},
    ...
]
```

### Добавление новой реализации

Для создания Real реализации:

1. Создайте класс наследующий `StatCollector`
2. Реализуйте метод `get_stats(period)`
3. Обновите `app.py` для использования новой реализации

```python
from .real_stat_collector import RealStatCollector

def get_stat_collector() -> StatCollector:
    if config.stat_collector_type == "real":
        return RealStatCollector(database_client)
    return MockStatCollector()
```

## Тестирование

### Unit тесты

```bash
# Запустить все тесты
make test

# Только тесты API
pytest tests/test_mock_stat_collector.py tests/test_api.py
```

### Integration тесты

Integration тесты проверяют работу API endpoints с реальными HTTP запросами.

## Документация

- **Полная спецификация**: [frontend/doc/api-specification.md](../../frontend/doc/api-specification.md)
- **Требования к дашборду**: [frontend/doc/dashboard-requirements.md](../../frontend/doc/dashboard-requirements.md)
- **Swagger UI**: http://localhost:8000/docs (при запущенном сервере)

## Известные ограничения

- Mock данные генерируются случайно при каждом запуске
- Нет персистентности данных между перезапусками
- Нет аутентификации (MVP версия)
- Нет rate limiting
- Только предустановленные периоды (day/week/month)

## Roadmap

- [ ] Реализация Real StatCollector с подключением к БД
- [ ] Добавление аутентификации (API Keys)
- [ ] Реализация rate limiting
- [ ] Кэширование результатов
- [ ] Websocket для real-time обновлений
- [ ] Prometheus метрики
- [ ] Docker контейнеризация

## Помощь

При возникновении проблем:

1. Проверьте, что сервер запущен: `curl http://localhost:8000/health`
2. Откройте документацию: http://localhost:8000/docs
3. Проверьте логи сервера
4. Убедитесь, что порт 8000 не занят другим процессом

## Лицензия

Часть проекта systech-aidd.

