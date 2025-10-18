# План реализации FS-003: Дашборд статистики диалогов

## Цели спринта

1. Реализовать полнофункциональный дашборд статистики диалогов согласно требованиям
2. Интегрировать дашборд с Mock API для получения данных
3. Реализовать визуализацию данных через график Timeline (Recharts)
4. Добавить фильтрацию по периодам (day/week/month)
5. Обеспечить адаптивный и производительный UI

## Архитектура решения

### Компоненты

```
frontend/
├── app/dashboard/page.tsx           # Главная страница дашборда (Server Component)
├── components/dashboard/
│   ├── metric-card.tsx              # ✅ Готов (требуется адаптация)
│   ├── timeline-chart.tsx           # ❌ Требуется реализация с Recharts
│   ├── recent-dialogs.tsx           # ✅ Готов (требуется интеграция с API)
│   ├── top-users.tsx                # ✅ Готов (требуется интеграция с API)
│   └── period-filter.tsx            # ❌ Новый компонент для фильтрации
├── lib/
│   ├── api.ts                       # ✅ Готов (fetchStats)
│   └── format-utils.ts              # ❌ Утилиты форматирования (даты, числа)
└── hooks/
    └── use-stats.ts                 # ❌ Хук для работы со статистикой
```

### Технологический стек

- **Фреймворк**: Next.js 15 с App Router
- **Графики**: Recharts (из shadcn/ui charts)
- **UI компоненты**: shadcn/ui (Card, Badge, Tabs, Skeleton)
- **Стилизация**: Tailwind CSS
- **Типизация**: TypeScript

## Детальный план реализации

### 1. Подготовка инфраструктуры

#### 1.1 Установка зависимостей

**Шаг 1: Установка компонента Tabs из shadcn/ui**

```bash
cd frontend
npx shadcn@latest add tabs
```

Это установит:

- `@radix-ui/react-tabs` - базовый компонент Radix UI
- `components/ui/tabs.tsx` - styled компонент shadcn/ui

**Шаг 2: Установка библиотек для графиков и дат**

```bash
pnpm add recharts date-fns
```

После установки в `package.json` будут добавлены:

- `recharts: ^2.10.3` - библиотека для интерактивных графиков
- `date-fns: ^2.30.0` - библиотека для работы с датами и форматирования

#### 1.2 Утилиты форматирования

Создать `frontend/lib/format-utils.ts`:

- `formatNumber(value: number)` - форматирование чисел с разделителями
- `formatDate(date: string, format: string)` - форматирование дат через date-fns
- `formatRelativeTime(date: string)` - относительное время ("2 minutes ago")
- `formatPercentage(value: number)` - форматирование процентов

### 2. Реализация хука для работы с API

Создать `frontend/hooks/use-stats.ts`:

```typescript
import { useState, useEffect } from 'react';
import { fetchStats } from '@/lib/api';
import type { StatsResponse, Period } from '@/types/api';

export function useStats(initialPeriod: Period = 'day') {
  const [period, setPeriod] = useState<Period>(initialPeriod);
  const [data, setData] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    // Загрузка данных при изменении периода
  }, [period]);

  return { data, loading, error, period, setPeriod };
}
```

**Особенности:**

- Автоматическая загрузка при изменении периода
- Обработка состояний loading/error
- Типизация ответов

### 3. Компонент фильтра периодов

Создать `frontend/components/dashboard/period-filter.tsx`:

```typescript
<Tabs defaultValue="day" value={period} onValueChange={setPeriod}>
  <TabsList className="grid w-full grid-cols-3">
    <TabsTrigger value="day">Day</TabsTrigger>
    <TabsTrigger value="week">Week</TabsTrigger>
    <TabsTrigger value="month">Month</TabsTrigger>
  </TabsList>
</Tabs>
```

**Требования:**

- Использовать shadcn/ui Tabs компонент
- Синхронизация с URL query params (period=day/week/month)
- Визуальная индикация активного периода

### 4. Обновление MetricCard компонента

Адаптировать `frontend/components/dashboard/metric-card.tsx`:

- Использовать данные из API вместо mock данных
- Добавить форматирование чисел через `formatNumber()`
- Улучшить отображение трендов (цвета, иконки)
- Добавить плавные анимации при обновлении значений

### 5. Реализация Timeline Chart

Полностью переписать `frontend/components/dashboard/timeline-chart.tsx`:

```typescript
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import type { TimelinePoint } from '@/types/api';

export function TimelineChart({ data, period }: { data: TimelinePoint[], period: Period }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Activity Timeline</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="timestamp" tickFormatter={formatTimestamp} />
            <YAxis />
            <Tooltip content={<CustomTooltip />} />
            <Line type="monotone" dataKey="value" stroke="#8884d8" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
```

**Особенности:**

- Адаптивная высота (300px для desktop)
- Форматирование оси X в зависимости от периода:
  - Day: "14:00" (часы)
  - Week: "Mon 17" (день недели + дата)
  - Month: "Oct 17" (месяц + день)
- Кастомный Tooltip с деталями
- Плавная линия с заливкой области под графиком
- Интерактивность при наведении

### 6. Обновление RecentDialogs компонента

Адаптировать `frontend/components/dashboard/recent-dialogs.tsx`:

- Использовать `data.recent_dialogs` из API
- Форматировать `last_activity` через `formatRelativeTime()`
- Добавить Skeleton для состояния загрузки
- Обработать пустое состояние (нет диалогов)
- Максимум 10 диалогов согласно требованиям

### 7. Обновление TopUsers компонента

Адаптировать `frontend/components/dashboard/top-users.tsx`:

- Использовать `data.top_users` из API
- Добавить визуальное выделение топ-3 пользователей (иконки Crown/Medal/Award)
- Форматировать количество сообщений через `formatNumber()`
- Добавить Skeleton для состояния загрузки
- Обработать пустое состояние (нет пользователей)

### 8. Обновление главной страницы дашборда

Переписать `frontend/app/dashboard/page.tsx`:

```typescript
'use client';

import { useStats } from '@/hooks/use-stats';
import { PeriodFilter } from '@/components/dashboard/period-filter';
// ... остальные импорты

export default function DashboardPage() {
  const { data, loading, error, period, setPeriod } = useStats('day');

  if (error) return <ErrorState error={error} />;

  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <div className="space-y-6">
            {/* Заголовок и фильтр */}
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold">Dashboard</h1>
                <p className="text-muted-foreground">Monitor AI conversation metrics</p>
              </div>
              <PeriodFilter period={period} onPeriodChange={setPeriod} />
            </div>

            {/* Контент с обработкой состояний */}
            {loading ? <DashboardSkeleton /> : (
              <>
                {/* Метрики */}
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                  {data?.metrics.map((metric, i) => (
                    <MetricCard key={i} {...metric} />
                  ))}
                </div>

                {/* График */}
                <TimelineChart data={data?.timeline || []} period={period} />

                {/* Нижняя часть */}
                <div className="grid gap-4 md:grid-cols-2">
                  <RecentDialogs dialogs={data?.recent_dialogs || []} />
                  <TopUsers users={data?.top_users || []} />
                </div>
              </>
            )}
          </div>
        </main>
        <Footer />
      </div>
    </div>
  );
}
```

**Требования:**

- Использовать 'use client' для клиентского компонента
- Обработка состояний loading/error/success
- Skeleton компоненты во время загрузки
- Передача данных из хука в компоненты

### 9. Компоненты состояний

#### 9.1 DashboardSkeleton

Расширить существующий `DashboardSkeleton` в `page.tsx`:

- Skeleton для фильтра периодов
- 4 Skeleton для метрик
- Skeleton для графика (высота 300px)
- 2 Skeleton для нижней части (Recent Dialogs, Top Users)

#### 9.2 ErrorState

Создать компонент для отображения ошибок:

```typescript
function ErrorState({ error }: { error: Error }) {
  return (
    <div className="flex h-full items-center justify-center">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Failed to load dashboard</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">{error.message}</p>
          <Button onClick={() => window.location.reload()}>Retry</Button>
        </CardContent>
      </Card>
    </div>
  );
}
```

#### 9.3 EmptyState

Компоненты для пустых состояний в RecentDialogs и TopUsers.

### 10. Синхронизация с URL

Обновить `page.tsx` для работы с URL query параметрами:

```typescript
'use client';

import { useSearchParams, useRouter } from 'next/navigation';

// В компоненте
const searchParams = useSearchParams();
const router = useRouter();
const initialPeriod = (searchParams.get('period') || 'day') as Period;

const { data, loading, error, period, setPeriod } = useStats(initialPeriod);

// При изменении периода обновлять URL
const handlePeriodChange = (newPeriod: Period) => {
  setPeriod(newPeriod);
  router.push(`/dashboard?period=${newPeriod}`);
};
```

### 11. Тестирование

#### 11.1 Ручное тестирование

- [ ] Запустить Mock API: `make run-api`
- [ ] Запустить frontend: `make run-frontend`
- [ ] Проверить загрузку дашборда на http://localhost:3000/dashboard
- [ ] Проверить переключение периодов (day/week/month)
- [ ] Проверить корректность отображения всех метрик
- [ ] Проверить работу графика Timeline
- [ ] Проверить списки Recent Dialogs и Top Users
- [ ] Проверить адаптивность на разных разрешениях
- [ ] Проверить состояния loading/error

#### 11.2 Сценарии тестирования

1. **Загрузка данных за день**: период=day, 24 точки на графике
2. **Загрузка данных за неделю**: период=week, 7 точек на графике
3. **Загрузка данных за месяц**: период=month, 30 точек на графике
4. **Переключение периодов**: плавный переход, обновление всех компонентов
5. **Ошибка API**: Mock API выключен - должен отобразиться ErrorState
6. **Медленное соединение**: проверка Skeleton компонентов

### 12. Оптимизация производительности

#### 12.1 Мемоизация компонентов

Использовать `React.memo` для дорогих компонентов:

- `MetricCard`
- `TimelineChart`
- `RecentDialogs`
- `TopUsers`

#### 12.2 Дебаунсинг

Для переключения периодов добавить небольшую задержку (200ms) перед запросом к API.

### 13. Документация

#### 13.1 Отчет о спринте

Создать `frontend/doc/sprint-fs003-report.md`:

- Цели и выполненные задачи
- Структура компонентов
- Примеры использования
- Скриншоты (опционально)
- Известные ограничения MVP
- Следующие шаги

#### 13.2 Обновление roadmap

Обновить `doc/frontend-roadmap.md`:

- Изменить статус FS-003 на "✅ Completed"
- Добавить ссылку на отчет
- Обновить дату завершения

## Структура итогового проекта

```
frontend/
├── app/
│   └── dashboard/
│       └── page.tsx                 # ✅ Обновлен (интеграция с API)
├── components/
│   ├── dashboard/
│   │   ├── metric-card.tsx          # ✅ Обновлен (форматирование)
│   │   ├── timeline-chart.tsx       # ✅ Реализован (Recharts)
│   │   ├── recent-dialogs.tsx       # ✅ Обновлен (API данные)
│   │   ├── top-users.tsx            # ✅ Обновлен (API данные)
│   │   └── period-filter.tsx        # ✅ Создан
│   ├── layout/                      # Без изменений
│   └── ui/                          # Без изменений
├── hooks/
│   └── use-stats.ts                 # ✅ Создан
├── lib/
│   ├── api.ts                       # Без изменений
│   ├── constants.ts                 # Без изменений
│   ├── utils.ts                     # Без изменений
│   └── format-utils.ts              # ✅ Создан
├── types/
│   └── api.ts                       # Без изменений
└── doc/
    ├── sprint-fs003-report.md       # ✅ Создан
    └── plans/
        └── s3-dashboard-plan.md     # ✅ Создан (этот документ)
```

## Критерии завершения спринта

- [ ] Все компоненты дашборда реализованы и интегрированы с Mock API
- [ ] График Timeline работает корректно с Recharts
- [ ] Фильтрация по периодам (day/week/month) работает
- [ ] Синхронизация фильтра с URL query параметрами
- [ ] Обработаны все состояния: loading, error, empty, success
- [ ] Адаптивная верстка для разрешений от 1024px
- [ ] Форматирование дат, чисел, процентов работает корректно
- [ ] Документация обновлена (отчет, roadmap)
- [ ] Ручное тестирование пройдено успешно

## Известные ограничения MVP

В первой версии **не реализуется**:

- Real-time обновление данных (автообновление каждые N секунд)
- Экспорт данных в CSV/PDF
- Детальный просмотр отдельного диалога
- Кастомные временные диапазоны (только day/week/month)
- Фильтрация по конкретным пользователям
- Сравнение нескольких периодов
- Анимации при изменении метрик (будет в следующих версиях)

## Следующие шаги после завершения

### FS-004: Реализация ИИ-чата

- Интерактивный чат для администратора
- Запросы к статистике на естественном языке
- Text-to-SQL интеграция

### FS-005: Переход на реальный API

- Реализация Real StatCollector
- Интеграция с PostgreSQL базой данных
- Оптимизация запросов

