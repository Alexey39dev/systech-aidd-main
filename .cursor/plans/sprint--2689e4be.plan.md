<!-- 2689e4be-95a9-41c7-8ed8-6f32cea86841 8ff35bca-69f3-44f0-b8c7-1658df3b061e -->
# План спринта D1: Build & Publish

## Цель

Автоматическая сборка и публикация Docker образов в GitHub Container Registry (ghcr.io) с публичным доступом для использования в будущих спринтах D2 (ручной deploy) и D3 (авто deploy).

## Контекст

- В спринте D0 созданы Dockerfile для bot, api, frontend
- Образы собираются локально через `docker-compose up`
- Нужна автоматизация для публикации в ghcr.io
- Trigger: push в ветку `main`
- Образы публичные (доступны без авторизации)
- Тегирование: только `latest` (MVP подход)

## Структура файлов

```
.github/
  workflows/
    build.yml                           # GitHub Actions workflow
docker-compose.prod.yml                 # Compose файл для registry образов
devops/
  doc/
    plans/
      d1-build-publish.md              # Этот план
    reports/
      d1-testing-report.md             # Отчет о тестировании (создать после выполнения)
    guides/
      github-actions-intro.md          # Введение в GitHub Actions
```

## Этапы реализации

### 1. Создать документацию по GitHub Actions

**Файл:** `devops/doc/guides/github-actions-intro.md`

Краткая инструкция должна содержать:

- **Введение в GitHub Actions:**
                                                                                                                                - Что такое GitHub Actions и workflow
                                                                                                                                - Основные концепции: jobs, steps, actions, runners
                                                                                                                                - Структура workflow файла (.github/workflows/)

- **Triggers и события:**
                                                                                                                                - `push` - автоматический запуск при коммите в ветку
                                                                                                                                - `pull_request` - запуск при создании/обновлении PR
                                                                                                                                - `workflow_dispatch` - ручной запуск через UI
                                                                                                                                - Фильтрация по веткам и путям

- **Работа с Pull Request:**
                                                                                                                                - Как тестировать workflow через PR перед merge в main
                                                                                                                                - Создание тестовой ветки для проверки CI
                                                                                                                                - Проверка статуса сборки в PR

- **Matrix strategy:**
                                                                                                                                - Параллельная сборка нескольких образов
                                                                                                                                - Переменные matrix для разных сервисов
                                                                                                                                - Оптимизация времени сборки

- **Публикация в GitHub Container Registry:**
                                                                                                                                - Настройка авторизации через GITHUB_TOKEN
                                                                                                                                - Permissions для packages (read/write)
                                                                                                                                - Public vs Private образы
                                                                                                                                - Как сделать образы публичными после сборки

- **Docker layer caching:**
                                                                                                                                - GitHub Actions cache для ускорения сборки
                                                                                                                                - cache-from и cache-to параметры
                                                                                                                                - Экономия времени на повторных сборках

- **Примеры команд:**
                                                                                                                                - Локальная работа с образами из ghcr.io
                                                                                                                                - Pull, tag, push образов
                                                                                                                                - Проверка статуса workflow

Объем: 150-200 строк, практичный справочник для разработчиков.

### 2. Создать GitHub Actions workflow

**Файл:** `.github/workflows/build.yml`

```yaml
name: Build and Publish Docker Images

on:
  push:
    branches:
                  - main

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    strategy:
      matrix:
        service: [bot, api, frontend]
    
    steps:
                  - name: Checkout repository
        uses: actions/checkout@v4
      
                  - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
                  - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
                  - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-${{ matrix.service }}
          tags: |
            type=raw,value=latest
      
                  - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./Dockerfile.${{ matrix.service }}
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

**Ключевые особенности:**

- Trigger: push в `main` ветку
- Matrix strategy для параллельной сборки 3 образов
- GitHub Actions cache для ускорения сборки (cache-from/cache-to)
- Тегирование: `latest`
- Автоматическая публикация в ghcr.io
- Использование стандартного `GITHUB_TOKEN` (не требует дополнительных секретов)

### 3. Создать docker-compose.prod.yml

**Файл:** `docker-compose.prod.yml`

Версия docker-compose для использования образов из GitHub Container Registry:

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

  migrations:
    image: ghcr.io/[USERNAME]/systech-aidd-main-api:latest
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
    image: ghcr.io/[USERNAME]/systech-aidd-main-bot:latest
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
    image: ghcr.io/[USERNAME]/systech-aidd-main-api:latest
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
    image: ghcr.io/[USERNAME]/systech-aidd-main-frontend:latest
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

**Примечание:** `[USERNAME]` нужно заменить на актуальное имя пользователя GitHub (будет указано в инструкции).

### 4. Настроить публичный доступ к образам

После первой сборки образов через GitHub Actions необходимо:

1. Перейти в GitHub → Packages
2. Для каждого образа (bot, api, frontend):

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Открыть Package settings
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Изменить видимость на "Public"
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Сохранить изменения

Это позволит скачивать образы без авторизации через `docker pull`.

### 5. Тестирование локально

**Шаги проверки:**

1. Создать тестовую ветку и сделать тривиальное изменение
2. Сделать commit и push в `main`
3. Проверить запуск workflow в GitHub Actions
4. Дождаться успешной сборки всех 3 образов
5. Проверить наличие образов в GitHub Packages
6. Настроить публичный доступ к образам
7. Локально протестировать pull образов:
   ```bash
   docker pull ghcr.io/[USERNAME]/systech-aidd-main-bot:latest
   docker pull ghcr.io/[USERNAME]/systech-aidd-main-api:latest
   docker pull ghcr.io/[USERNAME]/systech-aidd-main-frontend:latest
   ```

8. Обновить `docker-compose.prod.yml` с реальным USERNAME
9. Запустить через `docker-compose -f docker-compose.prod.yml up`
10. Проверить работу всех сервисов

### 6. Обновить README.md

Добавить новую секцию после существующей секции "🐳 Запуск через Docker":

````markdown
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
````

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



````

**Примечание:** Заменить `[USERNAME]` на реальное имя пользователя GitHub.

### 7. Создать отчет о тестировании

**Файл:** `devops/doc/reports/d1-testing-report.md`

Отчет должен содержать:

- Результаты локального тестирования pull образов
- Скриншоты/логи успешной сборки в GitHub Actions
- Результаты запуска через `docker-compose.prod.yml`
- Проверка работоспособности всех сервисов
- Время сборки образов (с кешем и без)
- Размеры образов
- Известные проблемы (если есть)

### 8. Обновить devops-roadmap.md

Обновить статус спринта D1:

```markdown
| Код | Описание | Статус |
|-----|----------|--------|
| D1 | Build & Publish | ✅ Completed |
````

И добавить ссылку на план:

```markdown
## D1: Build & Publish

**Статус:** ✅ **Completed** ([дата])

**Реализовано:**
- ✅ GitHub Actions workflow для автоматической сборки
- ✅ Matrix strategy для параллельной сборки 3 образов
- ✅ Публикация в GitHub Container Registry (ghcr.io)
- ✅ Публичный доступ к образам (без авторизации)
- ✅ Docker layer caching для ускорения сборки
- ✅ docker-compose.prod.yml для использования registry образов
- ✅ Badge статуса сборки в README

**План реализации:** [d1-build-publish.md](plans/d1-build-publish.md)  
**Отчет о тестировании:** [d1-testing-report.md](reports/d1-testing-report.md)
```

### 9. Сохранить план

**Файл:** `devops/doc/plans/d1-build-publish.md`

Сохранить этот план в файл для документации.

## Проверка работоспособности

После выполнения всех этапов:

1. ✅ Push в `main` автоматически запускает сборку
2. ✅ GitHub Actions успешно собирает все 3 образа
3. ✅ Образы публикуются в ghcr.io с тегом `latest`
4. ✅ Образы доступны публично (без авторизации)
5. ✅ Локальный `docker pull` работает без логина
6. ✅ `docker-compose -f docker-compose.prod.yml up` запускает все сервисы
7. ✅ API доступен на http://localhost:8000/docs
8. ✅ Frontend доступен на http://localhost:3000
9. ✅ Badge статуса сборки отображается в README

## Ожидаемый результат

- ✅ Автоматическая сборка образов при push в `main`
- ✅ Публикация в GitHub Container Registry (ghcr.io)
- ✅ Публичный доступ к образам (без авторизации)
- ✅ Matrix strategy для параллельной сборки
- ✅ GitHub Actions cache для ускорения повторных сборок
- ✅ docker-compose.prod.yml для использования registry образов
- ✅ Документация по GitHub Actions
- ✅ Badge статуса сборки в README
- ✅ Готовность к спринтам D2 (ручной deploy) и D3 (авто deploy)

## Примечания

- **MVP подход**: Только `latest` тег (без SHA, версий, дат)
- **Без lint/tests**: Фокус на сборке и публикации (добавим позже)
- **Без security scanning**: Простота важнее (добавим позже)
- **Без multi-platform**: Только linux/amd64 (добавим позже при необходимости)
- **Публичные образы**: Не требуется авторизация для pull (удобно для MVP)
- **Кеширование**: GitHub Actions cache ускоряет повторные сборки
- **Параллельная сборка**: Matrix strategy собирает 3 образа одновременно

## Не включено в MVP (для будущих спринтов)

- Lint checks в CI
- Автоматические тесты в CI
- Security scanning (Trivy, Snyk)
- Multi-platform builds (linux/arm64)
- Версионирование образов (semver)
- Автоматический rollback при ошибках
- Notifications (Slack, Telegram)
- Metrics и monitoring сборок

### To-dos

- [ ] Создать devops/doc/guides/github-actions-intro.md с введением в GitHub Actions, triggers, matrix strategy, публикацию образов
- [ ] Создать .github/workflows/build.yml с matrix strategy для сборки 3 образов (bot, api, frontend)
- [ ] Создать docker-compose.prod.yml для использования образов из ghcr.io вместо локальной сборки
- [ ] Протестировать GitHub Actions: push в main, проверить сборку, настроить публичный доступ к образам
- [ ] Локально протестировать docker pull образов из ghcr.io и запуск через docker-compose.prod.yml
- [ ] Обновить README.md: добавить секцию с использованием образов из registry и badge статуса сборки
- [ ] Создать devops/doc/reports/d1-testing-report.md с результатами тестирования
- [ ] Обновить devops/doc/devops-roadmap.md: изменить статус D1 на ✅ Completed, добавить ссылки
- [ ] Сохранить план в devops/doc/plans/d1-build-publish.md