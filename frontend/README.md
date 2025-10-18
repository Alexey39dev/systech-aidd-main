# Frontend Dashboard - Systech AI Assistant

> **🎉 Спринт FS-003 завершён успешно!** Дашборд статистики диалогов полностью функционален и готов к использованию.  
> 📖 См. [**DASHBOARD-READY.md**](DASHBOARD-READY.md) для быстрого старта | [ЗАПУСК.md](ЗАПУСК.md) для устранения неполадок | [**Итоги спринта** ✅](doc/SPRINT-FS003-SUCCESS.md)

Веб-приложение для мониторинга и анализа диалогов с AI-ассистентом. Предоставляет интерактивный дашборд с метриками, графиками и детальной статистикой.

## 🚀 Технологический стек

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **UI Library**: shadcn/ui
- **Styling**: Tailwind CSS
- **Package Manager**: pnpm
- **Backend Integration**: REST API (FastAPI)

## 📋 Требования к системе

- **Node.js**: 18.0.0 или выше
- **pnpm**: 8.0.0 или выше
- **Backend API**: Запущенный Mock API сервер (порт 8000)

## 🛠️ Установка и запуск

### 1. Установка предварительных требований

```bash
# Установка Node.js 18+ (если не установлен)
# Скачайте с https://nodejs.org/ или используйте:
winget install OpenJS.NodeJS

# Установка pnpm (если не установлен) - опционально
npm install -g pnpm

# Проверка установки
node --version  # должно быть 18.0.0+
npm --version   # встроен в Node.js
```

**Примечание**: pnpm - опциональный менеджер пакетов. Можно использовать npm (встроен в Node.js).

### 2. Установка зависимостей

```bash
# Установка зависимостей проекта
pnpm install
```

### 2. Настройка переменных окружения

```bash
# Скопируйте файл с примером конфигурации
cp .env.example .env.local

# Отредактируйте .env.local при необходимости
```

**Переменные окружения:**

```env
# Backend API URL
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### 3. Запуск в режиме разработки

```bash
# Запуск frontend сервера
pnpm dev

# Приложение будет доступно на http://localhost:3000
```

### 4. Запуск backend API (в отдельном терминале)

```bash
# Из корневой директории проекта
make run-api

# API будет доступно на http://localhost:8000
```

## 📁 Структура проекта

```
frontend/
├── app/                      # App Router pages
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Home page
│   ├── dashboard/           # Dashboard pages
│   │   └── page.tsx         # Dashboard main page
│   └── globals.css          # Global styles
├── components/              # React components
│   ├── ui/                  # shadcn/ui components
│   ├── layout/              # Layout components
│   │   ├── header.tsx       # Header component
│   │   ├── sidebar.tsx      # Sidebar navigation
│   │   └── footer.tsx       # Footer component
│   └── dashboard/           # Dashboard-specific components
│       ├── metric-card.tsx  # Metric card component
│       ├── timeline-chart.tsx  # Timeline chart
│       ├── recent-dialogs.tsx  # Recent dialogs list
│       └── top-users.tsx    # Top users list
├── lib/                     # Utilities and helpers
│   ├── utils.ts             # General utilities
│   ├── api.ts               # API client functions
│   └── constants.ts         # App constants
├── types/                   # TypeScript definitions
│   ├── api.ts               # API response types
│   └── index.ts             # Exported types
├── public/                  # Static files
│   ├── favicon.ico         # Website favicon
│   ├── next.svg            # Next.js logo
│   ├── vercel.svg          # Vercel logo
│   └── README.md           # Public directory docs
└── doc/                     # Documentation
    ├── frontend-vision.md   # Technical vision
    ├── adr-tech-stack.md    # Technology decisions
    └── plans/               # Sprint plans
```

## 🎯 Доступные команды

### Разработка

```bash
pnpm dev          # Запуск dev сервера (http://localhost:3000)
pnpm build        # Сборка production версии
pnpm start        # Запуск production сервера
pnpm type-check   # Проверка TypeScript типов
```

### Качество кода

```bash
pnpm lint         # Проверка кода ESLint
pnpm lint:fix     # Автоисправление ESLint ошибок
pnpm format       # Форматирование кода Prettier
pnpm format:check # Проверка форматирования
```

### Через Makefile

**Из корневой директории:**

```bash
make install-frontend  # Установка зависимостей
make run-frontend      # Запуск dev сервера
make build-frontend    # Сборка production
make lint-frontend     # Линтинг кода
make format-frontend   # Форматирование кода
```

**Из frontend директории:**

```bash
make install           # Установка зависимостей
make dev              # Запуск dev сервера
make build            # Сборка production
make lint             # Линтинг кода
make format           # Форматирование кода
```

## 🔌 Интеграция с Backend API

### API Endpoints

Приложение интегрируется с Mock API, предоставляющим следующие endpoints:

- `GET /api/stats?period={day|week|month}` - Получение статистики диалогов
- `GET /health` - Health check API

### Типы данных

TypeScript типы синхронизированы с backend API схемами:

```typescript
// Пример использования API
import { fetchStats } from "@/lib/api";
import type { StatsResponse, Period } from "@/types/api";

const stats: StatsResponse = await fetchStats("day");
```

### Переменные окружения

- `NEXT_PUBLIC_API_BASE_URL` - Базовый URL backend API
- По умолчанию: `http://localhost:8000`

## 🎨 UI Components

### shadcn/ui компоненты

Проект использует следующие базовые компоненты:

- **Card** - Контейнеры для контента
- **Button** - Интерактивные кнопки
- **Badge** - Индикаторы и метки
- **Separator** - Разделители контента
- **Skeleton** - Загрузочные состояния

### Кастомные компоненты

- **MetricCard** - Карточка с метрикой и трендом
- **TimelineChart** - График активности (placeholder)
- **RecentDialogs** - Список последних диалогов
- **TopUsers** - Топ активных пользователей

## 📊 Функциональность

### Dashboard

- **Метрики**: 4 ключевые метрики с трендами
- **Timeline**: График активности по времени
- **Recent Dialogs**: Последние 10 диалогов
- **Top Users**: Топ 10 активных пользователей
- **Фильтрация**: По периодам (день/неделя/месяц)

### Планируемая функциональность

- **AI Chat**: Интерактивный чат с ассистентом
- **Real-time updates**: Live обновление данных
- **Advanced filtering**: Расширенные фильтры
- **Export data**: Экспорт данных

## 🧪 Тестирование

```bash
# Запуск тестов (когда будут добавлены)
pnpm test

# Запуск тестов с покрытием
pnpm test:coverage
```

## 📚 Документация

- [Frontend Vision](doc/frontend-vision.md) - Архитектурное видение
- [ADR Tech Stack](doc/adr-tech-stack.md) - Обоснование выбора технологий
- [API Specification](../frontend/doc/api-specification.md) - Спецификация API
- [Dashboard Requirements](doc/dashboard-requirements.md) - Требования к дашборду

## 🚀 Развертывание

### Production сборка

```bash
# Сборка оптимизированной версии
pnpm build

# Запуск production сервера
pnpm start
```

### Environment Variables

Для production настройте следующие переменные:

```env
NEXT_PUBLIC_API_BASE_URL=https://your-api-domain.com
```

## 🤝 Разработка

### Code Style

- **TypeScript**: Строгая типизация
- **ESLint**: Строгие правила кодирования
- **Prettier**: Автоматическое форматирование
- **Conventional Commits**: Стандартизированные коммиты

### Git Workflow

1. Создайте feature branch
2. Внесите изменения
3. Запустите `pnpm lint` и `pnpm type-check`
4. Создайте Pull Request

### Добавление новых компонентов

```bash
# Добавление shadcn/ui компонента
pnpm dlx shadcn@latest add [component-name]

# Создание кастомного компонента
# Следуйте структуре в components/
```

## 🐛 Отладка

### DevTools

- **React DevTools**: Для отладки компонентов
- **Next.js DevTools**: Встроенные инструменты Next.js
- **Browser DevTools**: Network, Console, Performance

### Логи

```bash
# Детальные логи Next.js
DEBUG=* pnpm dev

# Логи только для API
DEBUG=api pnpm dev
```

## 📞 Поддержка

При возникновении проблем:

1. Проверьте [документацию](doc/)
2. Убедитесь что backend API запущен
3. Проверьте переменные окружения
4. Запустите `pnpm type-check` и `pnpm lint`

## 📄 Лицензия

MIT License - см. [LICENSE](../LICENSE) файл в корне проекта.
