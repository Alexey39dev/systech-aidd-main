# Инструкции по установке и запуску Frontend проекта

## Предварительные требования

Для работы с frontend проектом необходимо установить:

### 1. Node.js 18+

```bash
# Windows (через winget)
winget install OpenJS.NodeJS

# Или скачайте с https://nodejs.org/
# Выберите LTS версию (рекомендуется 18.x или 20.x)
```

### 2. pnpm 8+

```bash
# После установки Node.js
npm install -g pnpm

# Проверка установки
node --version  # должно быть 18.0.0+
pnpm --version  # должно быть 8.0.0+
```

## Установка и запуск проекта

### 1. Установка зависимостей

```bash
# Из корневой директории проекта
make install-frontend

# Или из frontend директории
cd frontend
make install
# или
pnpm install
```

**Важно**: Если вы видите ошибки с отсутствующими модулями (например, `@radix-ui/react-slot`), выполните:

```bash
cd frontend
pnpm install
```

**Если ESLint показывает ошибки с Prettier или TypeScript**:

```bash
cd frontend
pnpm install
# Установит eslint-config-prettier и @typescript-eslint плагины
```

**Если ESLint не может найти TypeScript правила**:

```bash
cd frontend
pnpm install
# Установит @typescript-eslint/eslint-plugin и @typescript-eslint/parser
```

**Если есть предупреждения о версии TypeScript**:

```bash
cd frontend
pnpm install
# Обновит TypeScript до поддерживаемой версии
```

### 2. Запуск frontend

```bash
# Из корневой директории проекта
make run-frontend

# Или из frontend директории
cd frontend
make dev
# или
pnpm dev
```

### 3. Запуск backend API

```bash
# В другом терминале
make run-api
```

### 4. Открыть в браузере

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Проверка работоспособности

### 1. Проверка команд package.json

```bash
cd frontend

# Проверка линтинга
pnpm lint

# Проверка форматирования
pnpm format

# Проверка типов
pnpm type-check

# Сборка production
pnpm build

# Запуск production (после build)
pnpm start
```

### 2. Проверка API интеграции

```bash
# Проверить что API доступно
curl http://localhost:8000/api/stats?period=day

# Проверить health check
curl http://localhost:8000/health
```

### 3. Проверка frontend в браузере

1. Откройте http://localhost:3000
2. Перейдите на страницу Dashboard
3. Проверьте что все компоненты отображаются
4. Проверьте навигацию между страницами

## Возможные проблемы

### Node.js не найден

- Убедитесь что Node.js установлен: `node --version`
- Перезапустите терминал после установки
- Проверьте PATH переменную

### pnpm не найден

- Установите pnpm: `npm install -g pnpm`
- Убедитесь что npm работает: `npm --version`

### Ошибки при установке зависимостей

- Очистите кэш: `pnpm store prune`
- Удалите node_modules: `rm -rf node_modules`
- Переустановите: `pnpm install`

### Ошибки TypeScript

- Проверьте версию TypeScript: `pnpm tsc --version`
- Очистите кэш: `pnpm tsc --build --clean`

### CORS ошибки

- Убедитесь что backend API запущен на порту 8000
- Проверьте переменную NEXT_PUBLIC_API_BASE_URL в .env.local

## Структура проекта

```
frontend/
├── app/                 # Next.js App Router
├── components/          # React компоненты
├── lib/                # Утилиты и API клиент
├── types/              # TypeScript типы
├── public/             # Статические файлы
└── doc/                # Документация
```

## Команды разработки

```bash
# Разработка
make run-frontend       # Запуск dev сервера
make run-api           # Запуск backend API

# Качество кода
make lint-frontend     # Линтинг
make format-frontend   # Форматирование

# Сборка
make build-frontend    # Production сборка
```

## Поддержка

При возникновении проблем:

1. Проверьте что все предварительные требования установлены
2. Убедитесь что порты 3000 и 8000 свободны
3. Проверьте логи в терминале
4. Обратитесь к документации в `frontend/doc/`
