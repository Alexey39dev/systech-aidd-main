# Введение в GitHub Actions

## Что такое GitHub Actions

GitHub Actions — это платформа для автоматизации CI/CD (Continuous Integration/Continuous Deployment), встроенная в GitHub. Она позволяет автоматизировать задачи сборки, тестирования и развертывания прямо в репозитории.

### Основные концепции

- **Workflow** — автоматизированный процесс, состоящий из одного или нескольких заданий (jobs)
- **Job** — набор шагов (steps), выполняемых на одном и том же раннере (runner)
- **Step** — отдельная задача, которая может выполнять команды или использовать действия (actions)
- **Action** — переиспользуемая единица кода для выполнения конкретной задачи
- **Runner** — сервер, на котором выполняется workflow (GitHub-hosted или self-hosted)

### Структура workflow файла

Workflow файлы размещаются в директории `.github/workflows/` и имеют расширение `.yml` или `.yaml`.

```yaml
name: Workflow Name
on: [push, pull_request]
jobs:
  job-name:
    runs-on: ubuntu-latest
    steps:
      - name: Step name
        uses: action/name@version
```

## Triggers и события

### Основные типы триггеров

- **`push`** — автоматический запуск при коммите в ветку
  ```yaml
  on:
    push:
      branches: [main, develop]
  ```

- **`pull_request`** — запуск при создании/обновлении PR
  ```yaml
  on:
    pull_request:
      branches: [main]
  ```

- **`workflow_dispatch`** — ручной запуск через UI GitHub
  ```yaml
  on:
    workflow_dispatch:
  ```

### Фильтрация по веткам и путям

```yaml
on:
  push:
    branches: [main]
    paths: ['src/**', 'Dockerfile*']
  pull_request:
    branches: [main]
    paths-ignore: ['docs/**', '*.md']
```

## Работа с Pull Request

### Тестирование workflow через PR

1. **Создание тестовой ветки:**
   ```bash
   git checkout -b feature/test-ci
   git push -u origin feature/test-ci
   ```

2. **Создание Pull Request:**
   - Перейти в GitHub → Pull requests → New pull request
   - Выбрать base: `main`, compare: `feature/test-ci`
   - Создать PR

3. **Проверка статуса сборки:**
   - В PR будет показан статус workflow
   - Зеленый ✅ = успешно, красный ❌ = ошибка
   - Можно просмотреть логи выполнения

### Проверка статуса сборки в PR

- Статус отображается в разделе "Checks" PR
- Можно кликнуть на "Details" для просмотра логов
- PR нельзя merge, если workflow не прошел успешно

## Matrix strategy

### Параллельная сборка нескольких образов

Matrix strategy позволяет запускать один job несколько раз с разными параметрами:

```yaml
strategy:
  matrix:
    service: [bot, api, frontend]
    node-version: [16, 18, 20]
```

### Переменные matrix

В каждом запуске доступна переменная `${{ matrix.service }}`:

```yaml
- name: Build Docker image
  run: docker build -f Dockerfile.${{ matrix.service }} .
```

### Оптимизация времени сборки

- Matrix jobs выполняются параллельно
- Можно ограничить количество параллельных jobs: `max-parallel: 2`
- Можно исключить определенные комбинации: `exclude: [...]`

## Публикация в GitHub Container Registry

### Настройка авторизации

GitHub Container Registry (ghcr.io) использует GitHub токены для авторизации:

```yaml
- name: Log in to GitHub Container Registry
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

### Permissions для packages

Workflow должен иметь права на запись в packages:

```yaml
permissions:
  contents: read
  packages: write
```

### Public vs Private образы

- **Private** (по умолчанию) — требуют авторизации для pull
- **Public** — доступны без авторизации

### Как сделать образы публичными

После первой сборки:

1. Перейти в GitHub → Packages
2. Найти созданный пакет
3. Открыть Package settings
4. Изменить видимость на "Public"
5. Сохранить изменения

## Docker layer caching

### GitHub Actions cache

Кеширование Docker слоев ускоряет повторные сборки:

```yaml
- name: Build and push Docker image
  uses: docker/build-push-action@v5
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

### Параметры кеширования

- **`cache-from`** — откуда загружать кеш
- **`cache-to`** — куда сохранять кеш
- **`type=gha`** — использовать GitHub Actions cache
- **`mode=max`** — сохранять максимальное количество слоев

### Экономия времени

- Первая сборка: ~5-10 минут
- Повторная сборка с кешем: ~1-2 минуты
- Экономия: 70-80% времени

## Примеры команд

### Локальная работа с образами из ghcr.io

```bash
# Скачать образ
docker pull ghcr.io/username/repo-name:latest

# Запустить контейнер
docker run -d ghcr.io/username/repo-name:latest

# Просмотреть образы
docker images | grep ghcr.io

# Удалить образ
docker rmi ghcr.io/username/repo-name:latest
```

### Pull, tag, push образов

```bash
# Pull из registry
docker pull ghcr.io/username/repo-name:latest

# Создать локальный тег
docker tag ghcr.io/username/repo-name:latest my-app:latest

# Push в другой registry
docker push my-registry.com/my-app:latest
```

### Проверка статуса workflow

```bash
# Через GitHub CLI
gh run list
gh run view [run-id]

# Через API
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/owner/repo/actions/runs
```

## Полезные ссылки

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Matrix Strategy](https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs)
