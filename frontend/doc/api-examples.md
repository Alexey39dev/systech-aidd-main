# Примеры запросов к Dialog Statistics API

Коллекция готовых примеров запросов для тестирования API.

## cURL примеры

### Базовые запросы

```bash
# Получить статистику за день (по умолчанию)
curl -X GET "http://localhost:8000/api/stats"

# Получить статистику за неделю
curl -X GET "http://localhost:8000/api/stats?period=week"

# Получить статистику за месяц
curl -X GET "http://localhost:8000/api/stats?period=month"
```

### С форматированием вывода

```bash
# С использованием python json.tool
curl -s "http://localhost:8000/api/stats?period=day" | python -m json.tool

# С использованием jq (если установлен)
curl -s "http://localhost:8000/api/stats?period=week" | jq '.'

# Только метрики
curl -s "http://localhost:8000/api/stats?period=day" | jq '.metrics'

# Только timeline
curl -s "http://localhost:8000/api/stats?period=day" | jq '.timeline'

# Только топ пользователей
curl -s "http://localhost:8000/api/stats?period=month" | jq '.top_users'
```

### С заголовками

```bash
# С явным указанием Accept заголовка
curl -X GET "http://localhost:8000/api/stats?period=day" \
  -H "Accept: application/json" \
  -H "User-Agent: MyApp/1.0"

# С выводом заголовков ответа
curl -i "http://localhost:8000/api/stats?period=day"

# С подробным выводом (debug)
curl -v "http://localhost:8000/api/stats?period=day"
```

### Сохранение в файл

```bash
# Сохранить ответ в файл
curl "http://localhost:8000/api/stats?period=day" -o stats_day.json

# Сохранить для всех периодов
curl "http://localhost:8000/api/stats?period=day" -o stats_day.json
curl "http://localhost:8000/api/stats?period=week" -o stats_week.json
curl "http://localhost:8000/api/stats?period=month" -o stats_month.json
```

### Health Check

```bash
# Проверка работоспособности
curl "http://localhost:8000/health"

# С форматированием
curl -s "http://localhost:8000/health" | python -m json.tool
```

### Корневой endpoint

```bash
# Информация об API
curl "http://localhost:8000/"

# С форматированием
curl -s "http://localhost:8000/" | python -m json.tool
```

## HTTPie примеры

HTTPie - современная альтернатива cURL с более простым синтаксисом.

### Установка

```bash
pip install httpie
```

### Базовые запросы

```bash
# Получить статистику за день
http GET http://localhost:8000/api/stats

# С параметром period
http GET http://localhost:8000/api/stats period==day
http GET http://localhost:8000/api/stats period==week
http GET http://localhost:8000/api/stats period==month
```

### Фильтрация вывода

```bash
# Только метрики
http GET http://localhost:8000/api/stats period==day | jq '.metrics'

# Только первая метрика
http GET http://localhost:8000/api/stats period==day | jq '.metrics[0]'

# Количество точек в timeline
http GET http://localhost:8000/api/stats period==day | jq '.timeline | length'
```

### Health Check

```bash
http GET http://localhost:8000/health
```

## Python примеры

### Использование requests

```python
import requests

# Базовый запрос
response = requests.get("http://localhost:8000/api/stats", params={"period": "day"})
stats = response.json()

print(f"Period: {stats['period']}")
print(f"Metrics: {len(stats['metrics'])}")
print(f"Timeline points: {len(stats['timeline'])}")
print(f"Recent dialogs: {len(stats['recent_dialogs'])}")
print(f"Top users: {len(stats['top_users'])}")

# Обработка метрик
for metric in stats['metrics']:
    print(f"{metric['label']}: {metric['value']} ({metric['change']} {metric['trend']})")

# Обработка топ пользователей
for user in stats['top_users']:
    print(f"{user['username']}: {user['messages_count']} messages, {user['dialogs_count']} dialogs")
```

### С обработкой ошибок

```python
import requests

def get_stats(period="day"):
    """Получить статистику с обработкой ошибок."""
    try:
        response = requests.get(
            "http://localhost:8000/api/stats",
            params={"period": period},
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        print("Request timeout")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None

# Использование
stats = get_stats("week")
if stats:
    print(f"Active users: {stats['metrics'][1]['value']}")
```

### Асинхронный запрос (httpx)

```python
import asyncio
import httpx

async def get_stats_async(period="day"):
    """Асинхронное получение статистики."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/api/stats",
            params={"period": period}
        )
        return response.json()

# Использование
stats = asyncio.run(get_stats_async("month"))
print(stats)
```

### Множественные запросы параллельно

```python
import asyncio
import httpx

async def fetch_all_periods():
    """Получить статистику для всех периодов параллельно."""
    async with httpx.AsyncClient() as client:
        tasks = [
            client.get("http://localhost:8000/api/stats", params={"period": period})
            for period in ["day", "week", "month"]
        ]
        responses = await asyncio.gather(*tasks)
        return [r.json() for r in responses]

# Использование
all_stats = asyncio.run(fetch_all_periods())
for stats in all_stats:
    print(f"Period {stats['period']}: {stats['metrics'][1]['value']} active users")
```

## JavaScript примеры

### Использование fetch

```javascript
// Базовый запрос
fetch("http://localhost:8000/api/stats?period=day")
  .then((response) => response.json())
  .then((data) => {
    console.log("Period:", data.period);
    console.log("Metrics:", data.metrics);
    console.log("Timeline:", data.timeline);
  })
  .catch((error) => console.error("Error:", error));
```

### С async/await

```javascript
async function getStats(period = "day") {
  try {
    const response = await fetch(`http://localhost:8000/api/stats?period=${period}`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching stats:", error);
    return null;
  }
}

// Использование
const stats = await getStats("week");
if (stats) {
  console.log("Active Users:", stats.metrics[1].value);
  stats.top_users.forEach((user) => {
    console.log(`${user.username}: ${user.messages_count} messages`);
  });
}
```

### Использование axios

```javascript
import axios from "axios";

// Базовый запрос
const response = await axios.get("http://localhost:8000/api/stats", {
  params: { period: "day" },
});
console.log(response.data);

// С обработкой ошибок
try {
  const response = await axios.get("http://localhost:8000/api/stats", {
    params: { period: "month" },
    timeout: 5000,
  });

  const stats = response.data;
  console.log("Metrics:", stats.metrics);
} catch (error) {
  if (error.response) {
    console.error("Server error:", error.response.data);
  } else if (error.request) {
    console.error("No response received");
  } else {
    console.error("Error:", error.message);
  }
}
```

### Множественные запросы

```javascript
// Параллельные запросы для всех периодов
const periods = ["day", "week", "month"];

Promise.all(
  periods.map((period) =>
    fetch(`http://localhost:8000/api/stats?period=${period}`).then((r) => r.json())
  )
).then((allStats) => {
  allStats.forEach((stats) => {
    console.log(`${stats.period}: ${stats.metrics[1].value} active users`);
  });
});
```

## PowerShell примеры

```powershell
# Базовый запрос
Invoke-RestMethod -Uri "http://localhost:8000/api/stats?period=day" -Method Get

# С параметрами
$params = @{
    Uri = "http://localhost:8000/api/stats"
    Method = "Get"
    Body = @{ period = "week" }
}
Invoke-RestMethod @params

# Сохранение в файл
Invoke-RestMethod -Uri "http://localhost:8000/api/stats?period=day" | ConvertTo-Json -Depth 10 | Out-File stats.json

# Health check
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
```

## Автоматизация тестирования

### Bash скрипт

```bash
#!/bin/bash
# test_api.sh - Скрипт для тестирования всех endpoints

BASE_URL="http://localhost:8000"

echo "Testing Dialog Statistics API"
echo "=============================="

# Health check
echo -e "\n1. Health Check"
curl -s "$BASE_URL/health" | python -m json.tool

# Root endpoint
echo -e "\n2. Root Endpoint"
curl -s "$BASE_URL/" | python -m json.tool

# Stats for all periods
for period in day week month; do
    echo -e "\n3. Stats for period: $period"
    curl -s "$BASE_URL/api/stats?period=$period" | jq '.period, .metrics[0]'
done

echo -e "\nAll tests completed!"
```

### Python скрипт

```python
#!/usr/bin/env python3
"""test_api.py - Скрипт для тестирования API"""

import requests

BASE_URL = "http://localhost:8000"

def test_health():
    """Тест health check endpoint."""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✓ Health check passed")

def test_stats(period):
    """Тест stats endpoint для периода."""
    response = requests.get(f"{BASE_URL}/api/stats", params={"period": period})
    assert response.status_code == 200

    data = response.json()
    assert data["period"] == period
    assert len(data["metrics"]) == 4
    assert len(data["timeline"]) > 0

    print(f"✓ Stats for {period} passed")

if __name__ == "__main__":
    test_health()
    for period in ["day", "week", "month"]:
        test_stats(period)
    print("\n✓ All tests passed!")
```

## Makefile команды

Проект включает готовые Makefile команды:

```bash
# Запустить API сервер
make run-api

# Протестировать все endpoints
make test-api

# Открыть документацию
make api-docs
```

## Дополнительные инструменты

### Postman Collection

Создайте новую коллекцию в Postman и импортируйте:

```json
{
  "info": {
    "name": "Dialog Statistics API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Get Stats (Day)",
      "request": {
        "method": "GET",
        "url": "http://localhost:8000/api/stats?period=day"
      }
    },
    {
      "name": "Get Stats (Week)",
      "request": {
        "method": "GET",
        "url": "http://localhost:8000/api/stats?period=week"
      }
    },
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "http://localhost:8000/health"
      }
    }
  ]
}
```

### OpenAPI Import

Импортируйте OpenAPI schema в Postman/Insomnia:

**URL**: http://localhost:8000/openapi.json

Это автоматически создаст все endpoints с правильными параметрами.
