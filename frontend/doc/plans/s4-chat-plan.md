# План Спринта FS-004: Реализация ИИ-чата

## Обзор

Реализация полнофункционального веб-чата с ИИ-ассистентом, интегрированного в существующий дашборд. Чат будет доступен через отдельную страницу `/chat` и через floating button на Dashboard. Поддержка двух режимов: обычный чат с LLM и режим администратора с text-to-SQL для вопросов о статистике.

## Архитектурные решения

### Backend API

- Новый endpoint: `POST /api/chat/message` для отправки сообщений
- Использование существующих компонентов: `LLMClient`, `DialogManager`, `DatabaseClient`
- Сессии пользователей: идентификация через заголовок `X-Session-ID` или cookie
- Два режима работы: `normal` (обычный LLM) и `admin` (text-to-SQL)

### Frontend UI

- Отдельная страница `/chat` с полноэкранным чатом
- Floating button на Dashboard (правый нижний угол)
- Компонент чата на базе референса `21st-ai-chat.md`
- Toggle переключения между режимами (normal/admin)
- Адаптивный дизайн для мобильных устройств

### Text-to-SQL Pipeline (режим admin)

1. Пользователь задает вопрос на естественном языке
2. Backend формирует специальный промпт для LLM с контекстом БД схемы
3. LLM генерирует SQL запрос
4. Backend выполняет SQL запрос к БД
5. Результаты передаются обратно в LLM для форматирования ответа
6. Пользователь получает человекочитаемый ответ

## Детальный план реализации

### Фаза 1: Backend API для чата

**1.1. Pydantic схемы для Chat API**

- Создать `src/api/chat_schemas.py`:
  - `ChatMode` - enum для режимов ("normal", "admin")
  - `ChatMessageRequest` - входящий запрос (mode, message, session_id)
  - `ChatMessageResponse` - ответ (message, sql_query?, metadata)
  - `ChatHistoryResponse` - история диалога

**1.2. Менеджер сессий**

- Создать `src/api/session_manager.py`:
  - `SessionManager` - управление сессиями пользователей
  - Генерация `session_id` (UUID)
  - Привязка `session_id` к `user_id` в БД
  - Получение/создание пользователя по session_id

**1.3. Text-to-SQL обработчик**

- Создать `src/api/text_to_sql.py`:
  - `TextToSQLProcessor` - класс для обработки admin запросов
  - Метод `generate_sql(question: str) -> str` - генерация SQL через LLM
  - Метод `execute_sql(query: str) -> list[dict]` - выполнение SQL
  - Метод `format_results(results, question) -> str` - форматирование ответа
  - Промпт с описанием схемы БД (таблицы `users`, `messages`)
  - Валидация SQL (только SELECT запросы, запрет DROP/DELETE/UPDATE)

**1.4. Chat API endpoints**

- Обновить `src/api/app.py`:
  - `POST /api/chat/message` - отправка сообщения в чат
  - `GET /api/chat/history` - получение истории диалога
  - `DELETE /api/chat/history` - очистка истории
  - Интеграция с `LLMClient`, `DialogManager`, `TextToSQLProcessor`
  - Обработка двух режимов (normal/admin)

**1.5. Обновление конфигурации**

- Добавить в `src/config.py`:
  - `chat_enabled: bool` - включить/выключить чат API
  - `text_to_sql_enabled: bool` - включить режим администратора
  - `session_expire_hours: int` - время жизни сессии

### Фаза 2: Frontend компоненты чата

**2.1. Установка зависимостей**

- Установить `framer-motion` для анимаций
- Установить `lucide-react` (уже есть, проверить версию)

**2.2. Базовый компонент чата**

- Создать `frontend/components/chat/chat-card.tsx`:
  - Адаптировать референс из `21st-ai-chat.md`
  - Props: `mode`, `onModeChange`, `className`
  - State: messages, input, isTyping
  - Анимированный border и floating particles
  - Обработка отправки сообщений

**2.3. Компоненты сообщений**

- Создать `frontend/components/chat/message-item.tsx`:
  - Отображение одного сообщения (user/assistant)
  - Поддержка markdown форматирования
  - Кнопка копирования текста
  - Timestamp для сообщений

**2.4. Компонент переключения режимов**

- Создать `frontend/components/chat/mode-toggle.tsx`:
  - Toggle switch для normal/admin режима
  - Индикатор текущего режима
  - Иконки и описание режимов

**2.5. SQL Query Display (для admin режима)**

- Создать `frontend/components/chat/sql-display.tsx`:
  - Отображение SQL запроса с подсветкой синтаксиса
  - Collapsible компонент (можно свернуть)
  - Кнопка копирования SQL

**2.6. Floating Button**

- Создать `frontend/components/chat/floating-chat-button.tsx`:
  - Круглая кнопка в правом нижнем углу
  - Иконка чата + badge с уведомлениями (опционально)
  - Анимация появления при скролле
  - При клике - переход на `/chat`

### Фаза 3: Страница чата и API клиент

**3.1. API клиент для чата**

- Создать `frontend/lib/chat-api.ts`:
  - `sendMessage(message, mode, sessionId)` - отправка сообщения
  - `fetchHistory(sessionId)` - получение истории
  - `clearHistory(sessionId)` - очистка истории
  - Обработка ошибок
  - TypeScript типы для запросов/ответов

**3.2. Hook для чата**

- Создать `frontend/hooks/use-chat.ts`:
  - `useChat(mode)` - основной hook для работы с чатом
  - State: messages, loading, error, sessionId
  - Methods: sendMessage, clearHistory, setMode
  - Автоматическое получение sessionId из localStorage
  - Обработка состояний loading/error

**3.3. TypeScript типы**

- Обновить `frontend/types/api.ts`:
  - `ChatMode` - тип режима
  - `ChatMessage` - тип сообщения
  - `ChatMessageRequest` - запрос
  - `ChatMessageResponse` - ответ
  - `ChatSession` - сессия

**3.4. Страница чата**

- Создать `frontend/app/chat/page.tsx`:
  - Полноэкранный layout с чатом
  - Интеграция `ChatCard` компонента
  - Mode toggle в header
  - Адаптивная верстка
  - Кнопка "Back to Dashboard"

**3.5. Обновление констант**

- Обновить `frontend/lib/constants.ts`:
  - Добавить `API_ENDPOINTS.CHAT_MESSAGE`
  - Добавить `API_ENDPOINTS.CHAT_HISTORY`
  - Добавить `ROUTES.CHAT`

### Фаза 4: Интеграция и полировка

**4.1. Интеграция floating button**

- Обновить `frontend/app/dashboard/page.tsx`:
  - Добавить `FloatingChatButton` в конец компонента
  - Позиционирование: fixed, right-6, bottom-6
  - z-index для корректного отображения поверх контента

**4.2. Навигация**

- Обновить `frontend/components/layout/sidebar.tsx`:
  - Добавить ссылку на `/chat` в навигацию
  - Иконка чата

**4.3. Улучшения UX**

- Skeleton loader для чата
- Empty state (когда нет сообщений)
- Error state (при ошибке API)
- Автоскролл к новым сообщениям
- Индикатор печати "AI is typing..."

**4.4. Обновление документации**

- Создать `frontend/doc/sprint-fs004-report.md`:
  - Описание реализованной функциональности
  - Скриншоты/описание UI
  - Инструкции по использованию
  - Известные ограничения

### Фаза 5: Тестирование (опционально, если останется время)

**5.1. Backend тесты**

- Создать `tests/test_chat_api.py`:
  - Тесты для chat endpoints
  - Тесты для SessionManager
  - Тесты для TextToSQLProcessor

**5.2. E2E тестирование**

- Ручное тестирование chat flow
- Проверка обоих режимов (normal/admin)
- Тестирование на разных устройствах

## Streaming (отложено)

Streaming ответов будет реализован в следующем спринте, если потребуется. Текущая реализация использует обычные HTTP запросы с ожиданием полного ответа.

## Технические детали

### Схема БД (используем существующие таблицы)

```sql
-- Таблица users (уже существует)
-- Таблица messages (уже существует)
-- Новых таблиц не требуется
```

### Промпт для Text-to-SQL

```
You are a SQL expert. Generate PostgreSQL queries based on user questions.

Database schema:
- users (id, telegram_id, username, created_at, updated_at, is_deleted)
- messages (id, role, content, length, user_id, created_at, is_deleted)

Rules:
- Only SELECT queries allowed
- Always include LIMIT clause
- Filter out is_deleted = true
- Return valid PostgreSQL syntax

Question: {user_question}
```

## Ключевые файлы для реализации

**Backend (новые):**

- `src/api/chat_schemas.py` - Pydantic схемы
- `src/api/session_manager.py` - управление сессиями
- `src/api/text_to_sql.py` - text-to-SQL процессор
- `src/api/chat_endpoints.py` - chat endpoints (или добавить в app.py)

**Frontend (новые):**

- `frontend/components/chat/chat-card.tsx` - основной компонент чата
- `frontend/components/chat/message-item.tsx` - сообщение
- `frontend/components/chat/mode-toggle.tsx` - переключатель режима
- `frontend/components/chat/sql-display.tsx` - отображение SQL
- `frontend/components/chat/floating-chat-button.tsx` - floating button
- `frontend/app/chat/page.tsx` - страница чата
- `frontend/lib/chat-api.ts` - API клиент
- `frontend/hooks/use-chat.ts` - React hook

**Файлы для обновления:**

- `src/config.py` - добавить настройки чата
- `src/api/app.py` - добавить chat endpoints
- `frontend/lib/constants.ts` - добавить константы
- `frontend/types/api.ts` - добавить типы
- `frontend/app/dashboard/page.tsx` - добавить floating button
- `frontend/components/layout/sidebar.tsx` - добавить навигацию

## Критерии готовности

✅ Backend API `/api/chat/message` работает в обоих режимах

✅ Frontend компонент чата отображается корректно

✅ Floating button на Dashboard работает

✅ Страница `/chat` доступна и функциональна

✅ Режим администратора генерирует и выполняет SQL запросы

✅ История диалога сохраняется в БД

✅ Адаптивная верстка работает на мобильных устройствах

✅ Обработка ошибок работает корректно

### To-dos

- [ ] Создать Pydantic схемы для Chat API (chat_schemas.py)
- [ ] Реализовать SessionManager для управления пользовательскими сессиями
- [ ] Реализовать TextToSQLProcessor с генерацией SQL и валидацией
- [ ] Создать chat endpoints в FastAPI (POST /api/chat/message, GET /api/chat/history)
- [ ] Установить frontend зависимости (framer-motion)
- [ ] Создать компонент ChatCard на основе референса 21st-ai-chat.md
- [ ] Создать вспомогательные компоненты чата (MessageItem, ModeToggle, SQLDisplay)
- [ ] Реализовать API клиент для чата (chat-api.ts)
- [ ] Создать useChat hook для управления состоянием чата
- [ ] Создать страницу /chat с полноэкранным чатом
- [ ] Создать FloatingChatButton и интегрировать в Dashboard
- [ ] Обновить навигацию (добавить ссылку на /chat в sidebar)
- [ ] Добавить UX улучшения (skeleton, empty state, auto-scroll)
- [ ] Создать документацию спринта (sprint-fs004-report.md)
