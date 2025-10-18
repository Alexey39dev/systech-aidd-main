# Запуск Systech AI Assistant с Chat

## Быстрый запуск

### Windows
```bash
# Запустить оба сервиса одной командой
start-chat.bat
```

### Ручной запуск

#### 1. Backend API (порт 8000)
```bash
make run-api
```

#### 2. Frontend (порт 3000)
```bash
cd frontend
npm run dev
```

## Доступ к приложению

- **Frontend Dashboard**: http://localhost:3000/dashboard
- **Chat Page**: http://localhost:3000/chat
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Функциональность

### Dashboard
- Статистика диалогов с AI-ассистентом
- Метрики, графики, топ пользователи
- Floating button для перехода в чат

### Chat
- **Обычный режим**: общение с LLM-ассистентом
- **Режим администратора**: вопросы о статистике с text-to-SQL
- Переключение режимов через toggle
- История диалогов
- Адаптивный дизайн

## API Endpoints

### Chat API
- `POST /api/chat/message` - отправка сообщения
- `GET /api/chat/history` - получение истории
- `DELETE /api/chat/history` - очистка истории

### Stats API
- `GET /api/stats?period={day|week|month}` - статистика диалогов
- `GET /health` - проверка состояния

## Требования

- Python 3.8+
- Зависимости установлены: `pip install -r requirements.txt`
- Frontend собран в `.next/` директории

## Устранение неполадок

1. **Backend не запускается**: проверьте, что все зависимости установлены
2. **Frontend не загружается**: убедитесь, что директория `.next/` существует
3. **Chat не работает**: проверьте, что backend API доступен на порту 8000
4. **framer-motion ошибки**: приложение работает с CSS анимациями, ошибки можно игнорировать
5. **404 на /chat**: убедитесь, что Next.js dev сервер запущен (не статический сервер)

## Структура проекта

```
├── src/api/                 # Backend API
│   ├── app.py              # FastAPI приложение
│   ├── chat_schemas.py     # Pydantic схемы для чата
│   ├── session_manager.py  # Управление сессиями
│   └── text_to_sql.py      # Text-to-SQL процессор
├── frontend/               # Frontend приложение
│   ├── app/chat/           # Страница чата
│   ├── components/chat/    # Компоненты чата
│   ├── hooks/use-chat.ts   # React hook для чата
│   └── lib/chat-api.ts     # API клиент
└── start-chat.bat          # Скрипт запуска
```
