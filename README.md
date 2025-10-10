# LLM-ассистент Telegram-бот

Простой LLM-ассистент, реализованный в виде Telegram-бота для ведения диалога с пользователями и ответов на их вопросы с заданной ролью через системный промпт.

## 🚀 Быстрый старт

### Предварительные требования

- Python 3.11+
- Telegram Bot Token (получить у [@BotFather](https://t.me/BotFather))
- OpenRouter API Key (получить на [openrouter.ai](https://openrouter.ai))

### Установка

1. **Клонируйте репозиторий:**
   ```bash
   git clone <repository-url>
   cd systech-aidd
   ```

2. **Установите зависимости:**
   ```bash
   make install
   ```

3. **Настройте конфигурацию:**
   ```bash
   cp .env.example .env
   # Отредактируйте .env файл, добавив ваши токены
   ```

4. **Запустите бота:**
   ```bash
   make run
   ```

## 📁 Структура проекта

```
systech-aidd/
├── src/                    # Исходный код
│   ├── bot.py             # TelegramBot класс
│   ├── llm_client.py      # LLMClient класс
│   ├── dialog_manager.py  # DialogManager класс
│   ├── config.py          # Config класс
│   └── logger.py          # Logger класс
├── tests/                 # Тесты
├── docs/                  # Документация
├── .env.example           # Пример конфигурации
├── pyproject.toml         # Конфигурация проекта
└── Makefile              # Команды сборки
```

## ⚙️ Конфигурация

Скопируйте `.env.example` в `.env` и настройте следующие параметры:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here

# OpenRouter API Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here

# LLM Configuration
SYSTEM_PROMPT=Ты полезный ассистент
MAX_HISTORY=10
LLM_MODEL=openai/gpt-3.5-turbo
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1000
```

## 🛠️ Команды разработки

```bash
make install    # Установить зависимости
make run        # Запустить бота
make test       # Запустить тесты
make clean      # Очистить временные файлы
make lint       # Проверить код
make format     # Форматировать код
```

## 📚 Документация

- [Идея проекта](docs/idea.md)
- [Техническое видение](docs/vision.md)
- [Правила разработки](docs/conventions.md)
- [План разработки](docs/tasklist.md)
- [Workflow](docs/workflow.md)

## 🎯 Особенности

- **Простота**: Минимальный MVP без оверинжиниринга
- **Асинхронность**: Высокая производительность
- **Модульность**: Четкое разделение ответственности
- **Гибкость**: Легкая настройка роли ассистента

## 📄 Лицензия

MIT License