# 🏗️ Обзор архитектуры

> Понимание архитектуры проекта за 30 минут

## Архитектурные принципы

### KISS (Keep It Simple, Stupid)
- Минимальный MVP без оверинжиниринга
- Только необходимая функциональность
- Понятный код

### ООП: 1 класс = 1 файл
- Четкое разделение ответственности
- Понятные имена файлов
- Легко найти нужный код

### SOLID
- **Single Responsibility** — каждый класс делает одно дело
- **Dependency Inversion** — зависимость от абстракций (Protocol)
- **Open/Closed** — легко расширять без изменения существующего кода

---

## Общая структура

```mermaid
graph TB
    User["👤 Пользователь<br/>(консоль)"]
    
    subgraph "UI Layer"
        Console["ConsoleApp<br/>console.py"]
    end
    
    subgraph "Business Logic"
        Dialog["DialogManager<br/>dialog_manager.py"]
        Role["RoleManager<br/>role_manager.py"]
    end
    
    subgraph "Integration Layer"
        LLM["LLMClient<br/>llm_client.py"]
        Retry["RetryUtils<br/>retry_utils.py"]
    end
    
    subgraph "Infrastructure"
        Config["Config<br/>config.py"]
        Logger["Logger<br/>logger.py"]
        Exceptions["Exceptions<br/>exceptions.py"]
        Messages["Messages<br/>messages.py"]
        Types["Types<br/>types.py"]
    end
    
    subgraph "External"
        API["OpenRouter API"]
        Files["📁 prompts/"]
    end
    
    User -->|ввод| Console
    Console -->|ответ| User
    Console --> Dialog
    Console --> Role
    Console --> LLM
    
    LLM --> Retry
    LLM --> API
    
    Role --> Files
    
    Dialog --> Types
    LLM --> Exceptions
    
    Console --> Config
    Console --> Logger
    Console --> Messages
    
    style User fill:#4a90e2,stroke:#2e5c8a,color:#fff
    style Console fill:#50c878,stroke:#2e7d4e,color:#fff
    style Dialog fill:#f39c12,stroke:#c87f0a,color:#fff
    style Role fill:#f39c12,stroke:#c87f0a,color:#fff
    style LLM fill:#e74c3c,stroke:#b03a2e,color:#fff
    style API fill:#95a5a6,stroke:#7f8c8d,color:#fff
    style Config fill:#9b59b6,stroke:#7d3c98,color:#fff
```

---

## Поток обработки запроса

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant C as ConsoleApp
    participant D as DialogManager
    participant R as RoleManager
    participant L as LLMClient
    participant A as OpenRouter API
    
    U->>C: Ввод сообщения
    
    C->>D: add_user_message()
    D-->>C: OK
    
    C->>R: get_system_prompt()
    R-->>C: Системный промпт
    
    C->>D: get_history()
    D-->>C: История диалога
    
    C->>L: get_response(message, prompt, history)
    
    alt Успешный запрос
        L->>A: API запрос
        A-->>L: Ответ
        L-->>C: Текст ответа
    else Ошибка (retry)
        L->>A: API запрос (попытка 1)
        A-->>L: Rate Limit Error
        Note over L: Ждём 1 сек
        L->>A: API запрос (попытка 2)
        A-->>L: Успех
        L-->>C: Текст ответа
    end
    
    C->>D: add_assistant_message()
    D-->>C: OK
    
    C->>U: Вывод ответа
    
    box rgba(74, 144, 226, 0.1) UI Layer
        participant C
    end
    
    box rgba(243, 156, 18, 0.1) Business Logic
        participant D
        participant R
    end
    
    box rgba(231, 76, 60, 0.1) Integration
        participant L
        participant A
    end
```

---

## Слои архитектуры

### 1. UI Layer (Пользовательский интерфейс)

**`ConsoleApp` (console.py)**
- Обработка ввода пользователя
- Парсинг команд (`/help`, `/history`, `/role`, `/stats`, `/clear`, `/exit`)
- Вывод ответов
- Координация компонентов

---

### 2. Business Logic (Бизнес-логика)

**`DialogManager` (dialog_manager.py)**
- Хранение истории диалога в памяти
- Автоматическая обрезка (trimming) при превышении `max_history`
- Статистика диалога

**`RoleManager` (role_manager.py)**
- Загрузка системных промптов из файлов (`prompts/`)
- Парсинг метаданных (название, описание)
- Предоставление информации о роли

---

### 3. Integration Layer (Интеграции)

**`LLMClient` (llm_client.py)**
- Интеграция с OpenRouter API через OpenAI SDK
- Формирование запросов с историей
- Обработка ответов

**`RetryUtils` (retry_utils.py)**
- Декоратор `with_exponential_backoff`
- Экспоненциальный backoff (1s → 2s → 4s)
- Максимум 3 попытки

---

### 4. Infrastructure (Инфраструктура)

**`Config` (config.py)**
- Загрузка конфигурации из `.env` через Pydantic
- Валидация параметров
- Значения по умолчанию

**`Logger` (logger.py)**
- Структурированное логирование через `structlog`
- Цветной вывод для консоли
- Опциональная запись в файл

**`Exceptions` (exceptions.py)**
- Иерархия кастомных исключений:
  - `AppError` (базовый)
    - `ConfigError`
    - `LLMError` → `LLMRateLimitError`, `LLMConnectionError`, `LLMTimeoutError`, ...
    - `RetryError`

**`Messages` (messages.py)**
- Enum классы для сообщений (DRY принцип):
  - `ErrorMessages` — ошибки
  - `InfoMessages` — информационные сообщения
  - `FallbackMessages` — fallback ответы при ошибках LLM

**`Types` (types.py)**
- `Message` (TypedDict) — типизированное сообщение
- `MessageRole` (Literal) — роль в диалоге (`"user"` | `"assistant"` | `"system"`)

---

## Управление зависимостями

```mermaid
graph LR
    Main["main.py"]
    Console["ConsoleApp"]
    Dialog["DialogManager"]
    Role["RoleManager"]
    LLM["LLMClient"]
    Config["Config"]
    
    Main --> Console
    Main --> Config
    
    Console --> Dialog
    Console --> Role
    Console --> LLM
    Console --> Config
    
    LLM --> Config
    Dialog --> Config
    
    style Main fill:#4a90e2,stroke:#2e5c8a,color:#fff
    style Console fill:#50c878,stroke:#2e7d4e,color:#fff
    style Dialog fill:#f39c12,stroke:#c87f0a,color:#fff
    style Role fill:#f39c12,stroke:#c87f0a,color:#fff
    style LLM fill:#e74c3c,stroke:#b03a2e,color:#fff
    style Config fill:#9b59b6,stroke:#7d3c98,color:#fff
```

**Принцип:** Зависимости идут сверху вниз (от UI к Infrastructure), никаких циклических зависимостей.

---

## Обработка ошибок

```mermaid
graph TD
    Start["Запрос к LLM"]
    Try["Попытка запроса"]
    Success{"Успех?"}
    RetryCheck{"Попыток < 3?"}
    Wait["Ждать (exponential backoff)"]
    HandleError["Обработать ошибку"]
    Fallback["Fallback сообщение"]
    Return["Вернуть ответ"]
    
    Start --> Try
    Try --> Success
    
    Success -->|Да| Return
    Success -->|Нет| RetryCheck
    
    RetryCheck -->|Да| Wait
    Wait --> Try
    
    RetryCheck -->|Нет| HandleError
    HandleError --> Fallback
    Fallback --> Return
    
    style Start fill:#4a90e2,stroke:#2e5c8a,color:#fff
    style Success fill:#50c878,stroke:#2e7d4e,color:#fff
    style HandleError fill:#e74c3c,stroke:#b03a2e,color:#fff
    style Fallback fill:#f39c12,stroke:#c87f0a,color:#fff
    style Return fill:#9b59b6,stroke:#7d3c98,color:#fff
```

---

## Асинхронность

Весь проект использует `async/await`:

- ✅ **Все I/O операции** — асинхронные
- ✅ **LLM запросы** — `await llm_client.get_response()`
- ✅ **Нет blocking операций** — используется `asyncio.sleep()` вместо `time.sleep()`

```python
# Пример: основной цикл приложения
async def run(self) -> None:
    while self.is_running:
        user_input = await asyncio.to_thread(input, "Вы: ")
        response = await self.get_response(user_input)
        print(f"Ассистент: {response}")
```

---

## Жизненный цикл приложения

```mermaid
stateDiagram-v2
    [*] --> Init: Запуск
    Init --> LoadConfig: Загрузка конфигурации
    LoadConfig --> SetupLogging: Настройка логов
    SetupLogging --> CreateApp: Создание ConsoleApp
    CreateApp --> Running: Запуск цикла
    
    Running --> ProcessInput: Ввод пользователя
    ProcessInput --> CheckCommand: Команда?
    
    CheckCommand --> ExecuteCommand: Да (/help, /role, ...)
    CheckCommand --> GetLLMResponse: Нет
    
    ExecuteCommand --> Running
    GetLLMResponse --> UpdateHistory: Добавить в историю
    UpdateHistory --> Running
    
    Running --> Shutdown: Ctrl+C или /exit
    Shutdown --> Cleanup: Очистка ресурсов
    Cleanup --> [*]
    
    note right of Running
        ApplicationContext
        обеспечивает graceful shutdown
    end note
```

---

## Точки расширения

### Как добавить новую команду

1. Добавить обработчик в `ConsoleApp.run()`
2. Добавить описание в `/help`
3. Написать тесты в `test_console.py`

### Как добавить нового LLM провайдера

1. Создать новый клиент (наследник `Protocol` для типизации)
2. Добавить параметры в `Config`
3. Обновить `LLMClient` или создать новый класс

### Как добавить новую роль

1. Создать файл в `prompts/my_role.txt`
2. Указать метаданные (`# Title:`, `# Description:`)
3. Установить `SYSTEM_PROMPT_FILE=prompts/my_role.txt` в `.env`

---

## Метрики качества

| Метрика | Значение | Статус |
|---------|----------|--------|
| **Test Coverage** | 87.59% | ✅ |
| **Tests Count** | 149 | ✅ |
| **Ruff Errors** | 0 | ✅ |
| **Mypy Errors** | 0 (strict mode) | ✅ |
| **Modules 100% coverage** | 6 из 11 | ✅ |

---

## 📚 Следующие шаги

- **[Тур по кодовой базе](03_codebase_tour.md)** — детальный обзор каждого модуля
- **[Модель данных](04_data_model.md)** — структуры данных и типизация
- **[Интеграции](05_integrations.md)** — работа с OpenRouter API

---

**⏱️ Время изучения:** 30 минут  
**🎯 Следующий гайд:** [Тур по кодовой базе →](03_codebase_tour.md)

