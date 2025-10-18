# Ручное развертывание SYSTECH-AIDD на Production сервер

## Обзор

Данная инструкция описывает пошаговый процесс развертывания системы SYSTECH-AIDD на production сервере 89.223.67.136 с использованием Docker образов из GitHub Container Registry.

**Параметры сервера:**
- Адрес: 89.223.67.136
- Пользователь: systech
- SSH ключ: systech_admin_key
- Рабочая директория: /opt/systech/dolgachev
- Порты: API 8002, Frontend 3002

---

## Раздел 1: Подготовка (локально)

### 1.1 Проверка SSH ключа

Убедитесь, что SSH ключ `systech_admin_key` находится в корневой директории проекта:

```bash
ls -la systech_admin_key
```

Если ключ отсутствует, скопируйте его из `c:\Users\a.dolgachev\Downloads\systech_admin_key` в текущую директорию.

Установите правильные права доступа:

```bash
# Windows (PowerShell)
icacls systech_admin_key /inheritance:r

# Linux/macOS
chmod 600 systech_admin_key
```

### 1.2 Создание файла .env

Скопируйте шаблон конфигурации:

```bash
# Windows
copy env.production.template .env

# Linux/macOS
cp env.production.template .env
```

Отредактируйте файл `.env` и заполните все обязательные значения:

```bash
# Windows
notepad .env

# Linux/macOS
nano .env
```

**Обязательные переменные для заполнения:**
- `OPENROUTER_API_KEY` - ваш API ключ от OpenRouter
- `POSTGRES_PASSWORD` - пароль для базы данных
- `JWT_SECRET_KEY` - случайная строка для JWT токенов
- `PASSWORD_SALT` - соль для хеширования паролей

**Пример заполнения:**
```env
OPENROUTER_API_KEY=sk-or-v1-1234567890abcdef...
POSTGRES_PASSWORD=SecurePassword123!
JWT_SECRET_KEY=my-super-secret-jwt-key-32-chars
PASSWORD_SALT=my-salt-16-chars
```

### 1.3 Проверка файлов конфигурации

Убедитесь, что все необходимые файлы присутствуют:

```bash
ls -la docker-compose.prod.yml
ls -la .env
ls -la prompts/
ls -la scripts/deploy-check.sh
```

### 1.4 Запуск скрипта проверки (опционально)

Запустите скрипт автоматической проверки готовности:

```bash
# Windows (PowerShell)
.\scripts\deploy-check.sh

# Linux/macOS
chmod +x scripts/deploy-check.sh
./scripts/deploy-check.sh
```

---

## Раздел 2: Подключение к серверу

### 2.1 SSH подключение

Подключитесь к серверу с использованием SSH ключа:

```bash
ssh -i systech_admin_key systech@89.223.67.136
```

**При первом подключении** система запросит подтверждение отпечатка ключа:
```
The authenticity of host '89.223.67.136 (89.223.67.136)' can't be established.
ED25519 key fingerprint is SHA256:5tuSFEjAxh6tJ97QJatvjfLSiyHRKWytaOOand762tg.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
```

### 2.2 Проверка Docker

Убедитесь, что Docker и Docker Compose установлены:

```bash
docker --version
docker compose version
```

**Ожидаемый вывод:**
```
Docker version 24.0.7, build afdd53b
Docker Compose version v2.21.0
```

### 2.3 Создание рабочей директории

Создайте рабочую директорию для проекта:

```bash
sudo mkdir -p /opt/systech/dolgachev
sudo chown systech:systech /opt/systech/dolgachev
cd /opt/systech/dolgachev
```

### 2.4 Проверка свободности портов

Убедитесь, что порты 8002 и 3002 свободны:

```bash
netstat -tuln | grep :8002
netstat -tuln | grep :3002
```

Если порты заняты, остановите соответствующие сервисы или выберите другие порты.

---

## Раздел 3: Копирование файлов на сервер

### 3.1 Копирование docker-compose.prod.yml

В новом терминале (не закрывая SSH сессию) скопируйте файл конфигурации:

```bash
scp -i systech_admin_key docker-compose.prod.yml systech@89.223.67.136:/opt/systech/dolgachev/
```

### 3.2 Копирование .env файла

```bash
scp -i systech_admin_key .env systech@89.223.67.136:/opt/systech/dolgachev/
```

### 3.3 Копирование директории prompts

```bash
scp -r -i systech_admin_key prompts/ systech@89.223.67.136:/opt/systech/dolgachev/
```

### 3.4 Проверка скопированных файлов

Вернитесь к SSH сессии и проверьте файлы:

```bash
ls -la /opt/systech/dolgachev/
```

**Ожидаемый результат:**
```
drwxr-xr-x 2 systech systech 4096 Dec 15 10:30 prompts
-rw-r--r-- 1 systech systech 1234 Dec 15 10:30 .env
-rw-r--r-- 1 systech systech 5678 Dec 15 10:30 docker-compose.prod.yml
```

---

## Раздел 4: Загрузка Docker образов

### 4.1 Pull образов из GitHub Container Registry

Загрузите все необходимые образы:

```bash
docker pull ghcr.io/dolgachev/bot:latest
docker pull ghcr.io/dolgachev/api:latest
docker pull ghcr.io/dolgachev/frontend:latest
```

### 4.2 Проверка загруженных образов

```bash
docker images | grep dolgachev
```

**Ожидаемый результат:**
```
ghcr.io/dolgachev/bot        latest    abc123def456   2 hours ago    150MB
ghcr.io/dolgachev/api        latest    def456ghi789   2 hours ago    200MB
ghcr.io/dolgachev/frontend   latest    ghi789jkl012   2 hours ago    300MB
```

---

## Раздел 5: Запуск сервисов

### 5.1 Запуск через Docker Compose

Запустите все сервисы в фоновом режиме:

```bash
docker compose -f docker-compose.prod.yml up -d
```

### 5.2 Проверка статуса сервисов

```bash
docker compose -f docker-compose.prod.yml ps
```

**Ожидаемый результат:**
```
NAME                     IMAGE                              COMMAND                  SERVICE     CREATED        STATUS                    PORTS
systech-aidd-postgres    postgres:16-alpine                 "docker-entrypoint.s…"   postgres   2 minutes ago  Up 2 minutes (healthy)    5432/tcp
systech-aidd-migrations  ghcr.io/dolgachev/api:latest       "python -m alembic u…"   migrations 2 minutes ago  Exited (0)               
systech-aidd-bot         ghcr.io/dolgachev/bot:latest       "python -m src.main"     bot        2 minutes ago  Up 2 minutes (healthy)    
systech-aidd-api         ghcr.io/dolgachev/api:latest       "python -m uvicorn s…"   api        2 minutes ago  Up 2 minutes (healthy)    0.0.0.0:8002->8000/tcp
systech-aidd-frontend    ghcr.io/dolgachev/frontend:latest  "pnpm dev"               frontend   2 minutes ago  Up 2 minutes (healthy)    0.0.0.0:3002->3000/tcp
```

### 5.3 Просмотр логов

Для мониторинга работы сервисов:

```bash
# Все сервисы
docker compose -f docker-compose.prod.yml logs -f

# Конкретный сервис
docker compose -f docker-compose.prod.yml logs -f api
docker compose -f docker-compose.prod.yml logs -f bot
docker compose -f docker-compose.prod.yml logs -f frontend
```

---

## Раздел 6: Миграции базы данных

### 6.1 Проверка завершения миграций

Миграции должны выполниться автоматически при запуске. Проверьте логи:

```bash
docker compose -f docker-compose.prod.yml logs migrations
```

**Ожидаемый результат:**
```
systech-aidd-migrations  | INFO  [alembic.runtime.migration] Context impl PostgreSQLImpl.
systech-aidd-migrations  | INFO  [alembic.runtime.migration] Will assume transactional DDL.
systech-aidd-migrations  | INFO  [alembic.runtime.migration] Running upgrade  -> 4b163d978e57, create users table
systech-aidd-migrations  | INFO  [alembic.runtime.migration] Running upgrade 4b163d978e57 -> 8c240cbf9c6f, create messages table
systech-aidd-migrations  | INFO  [alembic.runtime.migration] Running upgrade 8c240cbf9c6f -> 9df9e6f31a4e, add user_id to messages
```

### 6.2 Проверка таблиц в БД (опционально)

Подключитесь к базе данных для проверки:

```bash
docker exec -it systech-aidd-postgres psql -U aidd_user -d aidd_db
```

В PostgreSQL выполните:

```sql
\dt
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM messages;
\q
```

---

## Раздел 7: Проверка работоспособности

### 7.1 Проверка запущенных контейнеров

```bash
docker compose -f docker-compose.prod.yml ps
```

Все сервисы должны быть в статусе "Up" и "healthy".

### 7.2 Health Check API

```bash
curl http://89.223.67.136:8002/health
```

**Ожидаемый результат:**
```json
{"status": "healthy", "timestamp": "2024-12-15T10:30:00Z"}
```

### 7.3 Проверка API документации

Откройте в браузере: http://89.223.67.136:8002/docs

Должна открыться интерактивная документация Swagger UI.

### 7.4 Проверка Frontend

Откройте в браузере: http://89.223.67.136:3002

Должен загрузиться веб-интерфейс приложения.

### 7.5 Проверка Bot

Проверьте логи бота:

```bash
docker compose -f docker-compose.prod.yml logs bot
```

Бот должен быть запущен и готов к работе.

### 7.6 Проверка базы данных

```bash
# Количество записей в таблицах
docker exec systech-aidd-postgres psql -U aidd_user -d aidd_db -c "SELECT 'users' as table_name, COUNT(*) as count FROM users UNION ALL SELECT 'messages', COUNT(*) FROM messages;"
```

---

## Раздел 8: Troubleshooting

### 8.1 Распространенные проблемы

#### Проблема: Контейнеры не запускаются

**Решение:**
```bash
# Проверьте логи
docker compose -f docker-compose.prod.yml logs

# Перезапустите сервисы
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
```

#### Проблема: Ошибка подключения к базе данных

**Решение:**
```bash
# Проверьте статус PostgreSQL
docker compose -f docker-compose.prod.yml logs postgres

# Перезапустите PostgreSQL
docker compose -f docker-compose.prod.yml restart postgres
```

#### Проблема: API недоступен

**Решение:**
```bash
# Проверьте порты
netstat -tuln | grep :8002

# Проверьте логи API
docker compose -f docker-compose.prod.yml logs api

# Перезапустите API
docker compose -f docker-compose.prod.yml restart api
```

#### Проблема: Frontend не загружается

**Решение:**
```bash
# Проверьте логи Frontend
docker compose -f docker-compose.prod.yml logs frontend

# Проверьте переменную окружения
docker exec systech-aidd-frontend env | grep NEXT_PUBLIC_API_URL
```

### 8.2 Команды для отладки

```bash
# Статус всех сервисов
docker compose -f docker-compose.prod.yml ps

# Логи конкретного сервиса
docker compose -f docker-compose.prod.yml logs -f [service_name]

# Перезапуск сервиса
docker compose -f docker-compose.prod.yml restart [service_name]

# Остановка всех сервисов
docker compose -f docker-compose.prod.yml down

# Остановка с удалением volumes (ОСТОРОЖНО!)
docker compose -f docker-compose.prod.yml down -v
```

### 8.3 Обновление образов

```bash
# Остановить сервисы
docker compose -f docker-compose.prod.yml down

# Загрузить новые образы
docker pull ghcr.io/dolgachev/bot:latest
docker pull ghcr.io/dolgachev/api:latest
docker pull ghcr.io/dolgachev/frontend:latest

# Запустить сервисы
docker compose -f docker-compose.prod.yml up -d
```

---

## Заключение

После успешного выполнения всех шагов система SYSTECH-AIDD будет развернута на production сервере и доступна по следующим адресам:

- **API**: http://89.223.67.136:8002
- **API Docs**: http://89.223.67.136:8002/docs
- **Frontend**: http://89.223.67.136:3002
- **Bot**: Работает в фоновом режиме

Все сервисы настроены на автоматический перезапуск при сбоях и имеют health checks для мониторинга состояния.

---

## Дополнительные ресурсы

- [Docker Compose документация](https://docs.docker.com/compose/)
- [PostgreSQL документация](https://www.postgresql.org/docs/)
- [FastAPI документация](https://fastapi.tiangolo.com/)
- [Next.js документация](https://nextjs.org/docs)