<!-- ac61ba80-5b36-4e7a-9e5b-30b4becba8e1 8721641d-e70d-477c-839a-3ca18c003a01 -->

# План Спринта FS-002: Инициализация Frontend проекта

## Обзор

Создание каркаса frontend приложения на Next.js с полной настройкой инструментов разработки, документацией, базовой структурой страниц дашборда и интеграцией с Mock API.

## Этап 1: Документация проекта

### 1.1 Создание frontend-vision.md

- **Файл**: `frontend/doc/frontend-vision.md`
- **Содержание**:
  - Архитектурное видение UI приложения
  - Принципы разработки (компонентный подход, типизация, переиспользование)
  - Структура приложения и роутинг
  - Паттерны организации кода
  - Стратегия работы с данными (fetch, cache, state management)
  - UI/UX принципы и референсы

### 1.2 Создание ADR для технологического стека

- **Файл**: `frontend/doc/adr-tech-stack.md`
- **Содержание**:
  - Контекст и проблема выбора стека
  - Критерии выбора технологий
  - Рассмотренные альтернативы (Vite/Remix, Vue/Angular, Material-UI/Ant Design)
  - Обоснование выбора каждой технологии:
    - Next.js 15 - SSR, App Router, оптимизация
    - TypeScript - типобезопасность
    - shadcn/ui - кастомизируемые компоненты без vendor lock-in
    - Tailwind CSS - утилитарный подход, производительность
    - pnpm - быстрота, эффективность в монорепо
  - Последствия выбора
  - Дата решения и статус

### 1.3 Создание README.md для frontend

- **Файл**: `frontend/README.md`
- **Содержание**:
  - Обзор проекта и используемый стек
  - Требования к системе (Node.js 18+, pnpm 8+)
  - Пошаговая инструкция по установке
  - Команды для разработки (dev, build, start, lint, format, type-check)
  - Структура проекта с описанием директорий
  - Переменные окружения
  - Интеграция с Backend API
  - Ссылки на документацию

## Этап 2: Инициализация Next.js проекта

### 2.1 Проверка предустановленных инструментов

- Проверить наличие Node.js 18+ и pnpm 8+
- Если pnpm отсутствует, добавить инструкцию по установке в README

### 2.2 Создание Next.js приложения

- **Директория**: `frontend/`
- **Команда**: `pnpm create next-app@latest . --typescript --tailwind --app --eslint --import-alias "@/*"`
- **Параметры**:
  - TypeScript: Yes
  - ESLint: Yes
  - Tailwind CSS: Yes
  - `src/` directory: No (используем App Router напрямую)
  - App Router: Yes
  - Import alias: `@/*`

### 2.3 Настройка package.json

- Добавить/проверить скрипты:
  - `dev`: `next dev` (порт по умолчанию 3000)
  - `build`: `next build`
  - `start`: `next start`
  - `lint`: `next lint`
  - `format`: `prettier --write .`
  - `type-check`: `tsc --noEmit`
- Добавить метаданные проекта (name, version, description)

## Этап 3: Настройка shadcn/ui

### 3.1 Инициализация shadcn/ui

- **Команда**: `pnpm dlx shadcn@latest init`
- **Параметры** (из llms.txt):
  - Style: Default
  - Base color: Slate
  - CSS variables: Yes

### 3.2 Установка базовых компонентов

- Установить компоненты для дашборда:
  - `pnpm dlx shadcn@latest add card`
  - `pnpm dlx shadcn@latest add button`
  - `pnpm dlx shadcn@latest add badge`
  - `pnpm dlx shadcn@latest add separator`
  - `pnpm dlx shadcn@latest add skeleton`

### 3.3 Проверка конфигурации

- Проверить файлы:
  - `components.json` - конфигурация shadcn/ui
  - `lib/utils.ts` - функция `cn()` для объединения классов
  - `components/ui/` - установленные компоненты

## Этап 4: Структура проекта

### 4.1 Создание базовых директорий

```
frontend/
├── app/                      # App Router pages
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Home page
│   ├── dashboard/           # Dashboard pages
│   │   └── page.tsx         # Dashboard main page
│   └── globals.css          # Global styles
├── components/              # React components
│   ├── ui/                  # shadcn/ui components (auto-generated)
│   ├── layout/              # Layout components
│   │   ├── header.tsx       # Header component
│   │   ├── sidebar.tsx      # Sidebar navigation
│   │   └── footer.tsx       # Footer component
│   └── dashboard/           # Dashboard-specific components
│       ├── metric-card.tsx  # Metric card component
│       ├── timeline-chart.tsx  # Timeline chart placeholder
│       ├── recent-dialogs.tsx  # Recent dialogs list
│       └── top-users.tsx    # Top users list
├── lib/                     # Utilities and helpers
│   ├── utils.ts             # General utilities (shadcn)
│   ├── api.ts               # API client functions
│   └── constants.ts         # App constants
├── types/                   # TypeScript definitions
│   ├── api.ts               # API response types (from backend schemas)
│   └── index.ts             # Exported types
├── public/                  # Static files
│   ├── favicon.ico
│   └── images/
└── styles/                  # Additional styles (if needed)
```

### 4.2 Создание типов TypeScript

- **Файл**: `types/api.ts`
- **Содержание**: Типы на основе `frontend/doc/api-specification.md`:
  - `Period` = 'day' | 'week' | 'month'
  - `MetricCard` interface
  - `TimelinePoint` interface
  - `RecentDialog` interface
  - `TopUser` interface
  - `StatsResponse` interface

### 4.3 Создание API клиента

- **Файл**: `lib/api.ts`
- **Функции**:
  - `fetchStats(period: Period): Promise<StatsResponse>` - получение статистики
  - Обработка ошибок и fallback
  - Базовый URL из environment variables

### 4.4 Создание констант

- **Файл**: `lib/constants.ts`
- **Содержание**:
  - `API_BASE_URL` - URL backend API
  - `PERIODS` - доступные периоды фильтрации
  - `ROUTES` - маршруты приложения

## Этап 5: Базовые компоненты Layout

### 5.1 Root Layout

- **Файл**: `app/layout.tsx`
- **Функциональность**:
  - HTML структура с metadata
  - Подключение Tailwind CSS
  - Провайдеры (если нужны)
  - Общие настройки шрифтов

### 5.2 Header Component

- **Файл**: `components/layout/header.tsx`
- **Функциональность**:
  - Логотип/название приложения
  - Навигация по основным разделам
  - Placeholder для user menu (будущее)

### 5.3 Sidebar Component

- **Файл**: `components/layout/sidebar.tsx`
- **Функциональность**:
  - Навигационное меню
  - Активные ссылки с подсветкой
  - Ссылки: Dashboard, Chat (placeholder)

### 5.4 Footer Component (опционально)

- **Файл**: `components/layout/footer.tsx`
- **Функциональность**:
  - Копирайт
  - Ссылки на документацию

## Этап 6: Структура страниц дашборда

### 6.1 Home Page

- **Файл**: `app/page.tsx`
- **Содержание**:
  - Приветственная страница
  - Редирект на `/dashboard` или описание проекта
  - Использование компонентов shadcn/ui для демонстрации

### 6.2 Dashboard Page

- **Файл**: `app/dashboard/page.tsx`
- **Содержание**:
  - Layout с Header и Sidebar
  - Grid структура для размещения компонентов:
    - 4 метрика-карточки (верхняя строка)
    - Timeline график (средняя секция)
    - Recent Dialogs + Top Users (нижняя строка, 2 колонки)
  - Фильтр по периоду (day/week/month)
  - Пока без реальных данных, заглушки с skeleton

### 6.3 Dashboard Components (заглушки)

#### MetricCard Component

- **Файл**: `components/dashboard/metric-card.tsx`
- **Props**: `label`, `value`, `change`, `trend`
- **Функциональность**:
  - Отображение метрики в Card
  - Иконка тренда (стрелка вверх/вниз)
  - Цветовая индикация (green/red/neutral)
  - Использование shadcn/ui Card, Badge

#### TimelineChart Component

- **Файл**: `components/dashboard/timeline-chart.tsx`
- **Функциональность**:
  - Placeholder для графика
  - Текст "Chart will be here" или Skeleton
  - Подготовка структуры для будущей интеграции (recharts/chart.js)

#### RecentDialogs Component

- **Файл**: `components/dashboard/recent-dialogs.tsx`
- **Функциональность**:
  - Список диалогов в Card
  - Skeleton loading state
  - Структура: username, messages count, last activity

#### TopUsers Component

- **Файл**: `components/dashboard/top-users.tsx`
- **Функциональность**:
  - Список топ пользователей в Card
  - Skeleton loading state
  - Структура: username, messages count, dialogs count
  - Визуальное выделение топ-3

## Этап 7: Настройка Environment Variables

### 7.1 Создание .env.local

- **Файл**: `frontend/.env.local`
- **Содержание**:
  ```
  NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
  ```

### 7.2 Создание .env.example

- **Файл**: `frontend/.env.example`
- **Содержание**: Template для .env.local с комментариями

### 7.3 Обновление .gitignore

- Убедиться что `.env.local` в gitignore
- Добавить `.next/`, `node_modules/`, `out/`

## Этап 8: Линтинг и форматирование

### 8.1 Настройка Prettier

- **Файл**: `frontend/.prettierrc`
- **Конфигурация**:
  ```json
  {
    "semi": true,
    "singleQuote": false,
    "tabWidth": 2,
    "trailingComma": "es5",
    "printWidth": 100,
    "plugins": ["prettier-plugin-tailwindcss"]
  }
  ```

### 8.2 Установка prettier-plugin-tailwindcss

- `pnpm add -D prettier prettier-plugin-tailwindcss`

### 8.3 Настройка ESLint

- **Файл**: `frontend/.eslintrc.json`
- Проверить/дополнить конфигурацию:
  - Extends: `next/core-web-vitals`, `prettier`
  - Правила для TypeScript
  - Правила для React hooks

### 8.4 Создание скриптов проверки

- Добавить в package.json:
  - `lint:fix`: `next lint --fix`
  - `format:check`: `prettier --check .`

## Этап 9: TypeScript конфигурация

### 9.1 Проверка tsconfig.json

- **Файл**: `frontend/tsconfig.json`
- **Настройки**:
  - `strict: true`
  - `paths` для алиасов (`@/*`)
  - `incremental: true`
  - `esModuleInterop: true`

### 9.2 Создание type-check скрипта

- Уже добавлен в Этап 2.3

## Этап 10: Интеграция с Makefile

### 10.1 Добавление команд в корневой Makefile

- **Файл**: `Makefile`
- **Новые команды**:
  - `install-frontend`: Установка зависимостей frontend
  - `run-frontend`: Запуск frontend dev сервера
  - `build-frontend`: Сборка frontend production
  - `lint-frontend`: Линтинг frontend кода
  - `format-frontend`: Форматирование frontend кода
  - `test-frontend`: Запуск frontend тестов (placeholder)

### 10.2 Обновление команды help

- Добавить описание новых команд в секцию help

## Этап 11: Тестирование и проверка

### 11.1 Проверка установки зависимостей

- Запустить `make install-frontend`
- Проверить что все зависимости установлены без ошибок

### 11.2 Проверка запуска dev сервера

- Запустить `make run-frontend`
- Проверить доступность на `http://localhost:3000`
- Проверить что страницы открываются без ошибок

### 11.3 Проверка линтинга и форматирования

- Запустить `make lint-frontend`
- Запустить `make format-frontend`
- Убедиться что нет ошибок

### 11.4 Проверка type-check

- Запустить `pnpm type-check` в директории frontend
- Убедиться что нет ошибок типизации

### 11.5 Проверка сборки production

- Запустить `make build-frontend`
- Убедиться что сборка проходит успешно

### 11.6 Проверка всех команд package.json

- Последовательно запустить все команды из package.json
- Убедиться что каждая команда работает корректно:
  - `pnpm dev` - запуск dev сервера
  - `pnpm build` - сборка production
  - `pnpm start` - запуск production сервера (после build)
  - `pnpm lint` - линтинг без ошибок
  - `pnpm format` - форматирование кода
  - `pnpm type-check` - проверка типов

### 11.7 Тестирование подключения к Mock API

- Убедиться что Backend Mock API запущен (`make run-api`)
- Проверить доступность `http://localhost:8000/api/stats?period=day`
- Протестировать API клиент из frontend (через консоль браузера или test endpoint)
- Проверить CORS настройки при обращении с frontend
- Убедиться что переменная окружения `NEXT_PUBLIC_API_BASE_URL` корректно используется

## Этап 12: Финализация и документация

### 12.1 Создание отчёта о спринте

- **Файл**: `frontend/doc/sprint-fs002-report.md`
- **Содержание**:
  - Цели спринта и их достижение
  - Выполненные задачи с чеклистом
  - Созданная структура проекта
  - Установленные зависимости
  - Доступные команды
  - Скриншоты результата (опционально)
  - Следующие шаги для FS-003

### 12.2 Добавление ссылки на план в roadmap

- **Файл**: `doc/frontend-roadmap.md`
- Добавить ссылку на план `frontend/doc/plans/s2-init-plan.md` в таблицу спринтов (колонка "План реализации")
- Обновить статус FS-002 с "📋 Планируется" на "✅ Completed"

### 12.3 Актуализация roadmap после выполнения спринта

- **Файл**: `doc/frontend-roadmap.md`
- Добавить ссылку на отчёт спринта в таблицу
- Обновить дату завершения
- Проверить что следующий спринт FS-003 корректно описан

### 12.3 Проверка всей документации

- Убедиться что все ссылки работают
- Проверить корректность инструкций
- Проверить примеры кода

## Критерии завершения спринта

- ✅ Создана вся необходимая документация (vision, ADR, README)
- ✅ Next.js проект инициализирован с правильной конфигурацией
- ✅ shadcn/ui установлен и настроен
- ✅ Базовая структура директорий создана
- ✅ TypeScript типы для API определены
- ✅ API клиент создан (без реальных вызовов)
- ✅ Layout компоненты реализованы (Header, Sidebar)
- ✅ Структура страницы Dashboard создана с заглушками компонентов
- ✅ Все 4 dashboard компонента созданы (MetricCard, Timeline, RecentDialogs, TopUsers)
- ✅ Environment variables настроены
- ✅ Линтинг и форматирование настроены
- ✅ Команды в Makefile добавлены
- ✅ Dev сервер запускается без ошибок
- ✅ Production сборка работает
- ✅ Нет ошибок линтинга и type-check
- ✅ Отчёт о спринте создан
- ✅ Roadmap обновлён

## Зависимости и риски

**Зависимости:**

- Node.js 18+ и pnpm 8+ должны быть установлены
- Backend Mock API должно быть доступно (из FS-001)

**Риски:**

- Возможные проблемы совместимости версий Next.js 15 (новая версия)
- Необходимость настройки pnpm в Windows окружении

**Митигация:**

- Использовать LTS версии где возможно
- Детальная документация установки в README
- Тестирование на целевой платформе (Windows)

### To-dos

- [ ] Создать frontend-vision.md с архитектурным видением
- [ ] Создать adr-tech-stack.md с обоснованием выбора технологий
- [ ] Создать README.md с инструкциями по установке и запуску
- [ ] Инициализировать Next.js проект с TypeScript и Tailwind
- [ ] Установить и настроить shadcn/ui с базовыми компонентами
- [ ] Создать структуру директорий (app/, components/, lib/, types/, public/)
- [ ] Определить TypeScript типы для API на основе спецификации
- [ ] Создать API клиент с функциями для работы с backend
- [ ] Реализовать Layout компоненты (Header, Sidebar, Footer)
- [ ] Создать структуру страницы Dashboard с Grid layout
- [ ] Создать компоненты Dashboard (MetricCard, Timeline, RecentDialogs, TopUsers)
- [ ] Настроить environment variables (.env.local, .env.example)
- [ ] Настроить ESLint, Prettier и форматирование кода
- [ ] Добавить команды frontend в корневой Makefile
- [ ] Протестировать запуск, сборку, линтинг и type-check
- [ ] Создать отчёт о спринте и обновить roadmap
