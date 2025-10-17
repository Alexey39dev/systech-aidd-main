# 🧪 Тестирование и качество

> Философия тестирования и контроль качества за 30 минут

## Философия тестирования

### Что тестируем

- ✅ **Публичные API** — внешние интерфейсы классов/функций
- ✅ **Бизнес-логику** — критичные алгоритмы
- ✅ **Edge cases** — граничные значения, ошибки
- ✅ **Интеграции** — взаимодействие компонентов

### Что НЕ тестируем

- ❌ Приватные методы напрямую (тестируются через публичный API)
- ❌ Тривиальные getter/setter без логики
- ❌ Внешние библиотеки (используем моки)
- ❌ Код, который просто пробрасывает значения

---

## Инструменты

### pytest — фреймворк тестирования

```bash
# Установка
uv pip install -e ".[dev]"

# Запуск всех тестов
pytest

# Запуск с покрытием
pytest --cov=src --cov-report=term-missing

# Запуск одного файла
pytest tests/test_dialog_manager.py

# Запуск одного теста
pytest tests/test_dialog_manager.py::test_add_user_message

# С verbose
pytest -v

# Остановка на первой ошибке
pytest -x
```

---

### pytest-asyncio — async тесты

```python
import pytest

@pytest.mark.asyncio
async def test_llm_client_response():
    """Тест асинхронного метода."""
    client = LLMClient(config)
    response = await client.get_response("Test", "Prompt", [])
    assert isinstance(response, str)
```

---

### pytest-cov — покрытие кода

```bash
# Запуск с покрытием
pytest --cov=src --cov-report=term-missing

# HTML отчет
pytest --cov=src --cov-report=html

# Открыть отчет
open htmlcov/index.html  # macOS/Linux
start htmlcov/index.html  # Windows
```

**Пример вывода:**
```
Name                        Stmts   Miss  Cover   Missing
---------------------------------------------------------
src/config.py                  16      1    94%   59
src/console.py                144      1    99%   243
src/dialog_manager.py          38      0   100%
---------------------------------------------------------
TOTAL                         532     66    87.59%
```

---

### Ruff — линтер и форматтер

```bash
# Форматирование
ruff format src tests

# Проверка стиля
ruff check src tests

# Автоисправление
ruff check --fix src tests
```

**Конфигурация (`pyproject.toml`):**
```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "F",    # pyflakes
    "I",    # isort
    "N",    # pep8-naming
    "W",    # pycodestyle warnings
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "C4",   # flake8-comprehensions
    "SIM",  # flake8-simplify
]
```

---

### Mypy — проверка типов

```bash
# Проверка всех файлов
mypy src

# Проверка одного файла
mypy src/dialog_manager.py
```

**Конфигурация (`pyproject.toml`):**
```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

**Strict mode включает:**
- Обязательные type hints для всех функций
- Проверка типов возвращаемых значений
- Запрет `Any` без явного указания
- Проверка неиспользуемых игнорирований

---

## Структура тестов

### AAA Pattern (Arrange-Act-Assert)

```python
def test_add_user_message():
    # Arrange — подготовка
    manager = DialogManager(max_history=10)
    
    # Act — действие
    manager.add_user_message("Hello")
    
    # Assert — проверка
    assert len(manager) == 1
    assert manager.get_history()[0]["role"] == "user"
    assert manager.get_history()[0]["content"] == "Hello"
```

---

### Фикстуры для переиспользования

```python
import pytest
from src.config import Config
from src.console import ConsoleApp

@pytest.fixture
def config():
    """Фикстура для конфигурации."""
    return Config(
        openrouter_api_key="test-key",
        max_history=10,
        llm_model="openai/gpt-3.5-turbo",
    )

@pytest.fixture
def console_app(config):
    """Фикстура для ConsoleApp."""
    return ConsoleApp(config)

# Использование
def test_something(console_app):
    assert console_app.config.max_history == 10
```

---

### Параметризация

```python
import pytest

@pytest.mark.parametrize("max_history,expected_max_messages", [
    (1, 2),   # 1 пара = 2 сообщения
    (5, 10),  # 5 пар = 10 сообщений
    (10, 20), # 10 пар = 20 сообщений
    (50, 100),# 50 пар = 100 сообщений
])
def test_history_trimming(max_history, expected_max_messages):
    """Тест обрезки истории для разных значений max_history."""
    manager = DialogManager(max_history=max_history)
    
    # Добавить больше сообщений, чем лимит
    for i in range(expected_max_messages + 5):
        manager.add_user_message(f"Message {i}")
    
    # Проверить, что обрезано до лимита
    assert len(manager) == expected_max_messages
```

**Результат:**
```
test_history_trimming[1-2] PASSED
test_history_trimming[5-10] PASSED
test_history_trimming[10-20] PASSED
test_history_trimming[50-100] PASSED
```

---

## Типы тестов

### Unit тесты

**Цель:** Тестировать отдельные компоненты в изоляции

```python
def test_dialog_manager_initialization():
    """Тест инициализации DialogManager."""
    manager = DialogManager(max_history=15)
    
    assert manager.max_history == 15
    assert len(manager) == 0
    assert manager.get_history() == []
```

---

### Integration тесты

**Цель:** Тестировать взаимодействие компонентов

```python
@pytest.mark.asyncio
async def test_full_dialog_flow(console_app):
    """Интеграционный тест полного потока диалога."""
    # Arrange
    user_message = "Hello, how are you?"
    
    # Act
    response = await console_app.get_response(user_message)
    
    # Assert
    assert isinstance(response, str)
    assert len(response) > 0
    
    # Проверить, что сохранено в истории
    history = console_app.dialog_manager.get_history()
    assert len(history) == 2  # user + assistant
    assert history[0]["role"] == "user"
    assert history[0]["content"] == user_message
```

---

### Edge cases тесты

**Цель:** Проверить граничные значения и необычные сценарии

```python
@pytest.mark.parametrize("invalid_input", [
    "",           # Пустая строка
    "   ",        # Только пробелы
    "\n\n",       # Только переносы строк
    "\t\t",       # Только табуляции
])
def test_add_empty_message(invalid_input):
    """Тест добавления пустых/некорректных сообщений."""
    manager = DialogManager()
    
    manager.add_user_message(invalid_input)
    
    # Пустые сообщения не должны добавляться
    assert len(manager) == 0
```

---

### Error handling тесты

**Цель:** Проверить обработку ошибок

```python
@pytest.mark.asyncio
async def test_llm_rate_limit_error(console_app, mocker):
    """Тест обработки rate limit ошибки."""
    from openai import RateLimitError
    
    # Мокаем API, чтобы всегда возвращал ошибку
    mock_create = mocker.patch.object(
        console_app.llm_client.client.chat.completions,
        "create",
        side_effect=RateLimitError("Rate limit exceeded", response=None, body=None)
    )
    
    # Должен вернуть fallback сообщение после 3 попыток
    response = await console_app.get_response("Test message")
    
    assert "Извините" in response or "К сожалению" in response
    assert mock_create.call_count == 3  # 3 попытки
```

---

## Моки и стабы

### Когда использовать моки

- **Внешние API** — OpenRouter, HTTP запросы
- **Файловая система** — чтение/запись файлов
- **Время** — `asyncio.sleep`, таймауты
- **Случайность** — выбор fallback ответов

---

### Мокирование OpenAI API

```python
from unittest.mock import Mock, AsyncMock

@pytest.mark.asyncio
async def test_llm_client_with_mock(config):
    """Тест LLMClient с мокированным API."""
    client = LLMClient(config)
    
    # Создать мок ответа
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Mocked response"
    
    # Мокировать API вызов
    with patch.object(
        client.client.chat.completions,
        "create",
        new_callable=AsyncMock,
        return_value=mock_response
    ):
        response = await client.get_response("Test", "System", [])
        
        assert response == "Mocked response"
```

---

### Мокирование файловой системы

```python
from pathlib import Path
from unittest.mock import Mock, patch

def test_role_manager_with_mock_file(tmp_path):
    """Тест RoleManager с временным файлом."""
    # Создать временный файл
    prompt_file = tmp_path / "test_role.txt"
    prompt_file.write_text(
        "# Title: Test Role\n"
        "# Description: Test description\n\n"
        "You are a test assistant."
    )
    
    # Тестировать
    manager = RoleManager(prompt_file)
    role_info = manager.get_role_info()
    
    assert role_info["title"] == "Test Role"
    assert role_info["description"] == "Test description"
```

---

## Coverage Guidelines

### Целевые показатели

| Модуль | Целевой Coverage | Комментарий |
|--------|------------------|-------------|
| **Критичные** | 90-100% | dialog_manager, llm_client, role_manager |
| **Вспомогательные** | 80-90% | console, config, retry_utils |
| **Infrastructure** | 70-80% | logger, exceptions, messages, types |
| **Entry point** | 40-60% | main.py (не критично) |

---

### Текущее состояние

```
Name                        Stmts   Miss  Cover
-----------------------------------------------
src/dialog_manager.py          38      0   100%  ✅
src/exceptions.py              24      0   100%  ✅
src/types.py                    5      0   100%  ✅
src/messages.py                51      0   100%  ✅
src/logger.py                  65      0   100%  ✅
src/role_manager.py            58      0   100%  ✅
src/console.py                144      1    99%  ✅
src/llm_client.py              62      2    97%  ✅
src/config.py                  16      1    94%  ✅
src/retry_utils.py             29      3    90%  ✅
src/main.py                    98     59    40%  🟡
-----------------------------------------------
TOTAL                         532     66  87.59% ✅
```

---

### Исключения из покрытия

**`pyproject.toml`:**
```toml
[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.:",
    "raise NotImplementedError",
]
```

**Использование:**
```python
if TYPE_CHECKING:  # pragma: no cover
    from .types import Message

if __name__ == "__main__":  # pragma: no cover
    asyncio.run(main())
```

---

## Автоматизация проверок

### make quality — одна команда для всего

```bash
make quality
```

**Выполняет:**
1. ✅ `ruff format` — форматирование кода
2. ✅ `ruff check` — проверка стиля
3. ✅ `mypy src` — проверка типов
4. ✅ `pytest --cov=src` — запуск тестов + coverage

**Вывод:**
```
==========================================
Полная проверка качества кода
==========================================

1/4 Форматирование кода...
22 files reformatted

2/4 Проверка стиля...
All checks passed!

3/4 Проверка типов...
Success: no issues found in 11 source files

4/4 Запуск тестов...
===== 149 passed in 2.5s =====
Coverage: 87.59%

==========================================
✅ Все проверки завершены!
==========================================
```

---

### Отдельные команды

```bash
# Только форматирование
make format

# Только линтинг
make lint

# Только типы
make type-check

# Только тесты
make test
```

---

## Чек-лист перед коммитом

### ✅ Обязательно

```bash
# 1. Запустить полную проверку
make quality
# → Все проверки должны пройти (0 ошибок)
```

### ✅ Вручную проверить

- [ ] Все новые функции покрыты тестами
- [ ] Coverage не упал ниже 80%
- [ ] Все публичные методы имеют docstrings
- [ ] Все параметры типизированы
- [ ] Нет хардкода (константы вынесены)
- [ ] Нет дублирования кода (DRY)
- [ ] Соблюдены соглашения об именовании

---

## Best Practices

### ✅ Тестируй поведение, а не реализацию

```python
# ❌ Плохо: зависит от внутренней реализации
def test_implementation():
    manager = DialogManager()
    manager.add_user_message("Test")
    assert manager._messages[0]["role"] == "user"  # Приватное поле

# ✅ Хорошо: тестирует публичное поведение
def test_behavior():
    manager = DialogManager()
    manager.add_user_message("Test")
    history = manager.get_history()
    assert history[0]["role"] == "user"
```

---

### ✅ Независимые тесты

```python
# ✅ Хорошо: каждый тест независим
def test_a():
    manager = DialogManager()  # Новый экземпляр
    manager.add_user_message("Test A")
    assert len(manager) == 1

def test_b():
    manager = DialogManager()  # Новый экземпляр
    manager.add_user_message("Test B")
    assert len(manager) == 1
```

---

### ✅ Понятные assert сообщения

```python
# ✅ Хорошо: понятно, что пошло не так
assert len(history) == 2, f"Expected 2 messages, got {len(history)}"

# ❌ Плохо: непонятная ошибка
assert len(history) == 2
```

---

### ✅ DRY в тестах через фикстуры

```python
# ✅ Хорошо: фикстура для переиспользования
@pytest.fixture
def manager_with_messages():
    manager = DialogManager(max_history=10)
    manager.add_user_message("Hello")
    manager.add_assistant_message("Hi!")
    return manager

def test_a(manager_with_messages):
    assert len(manager_with_messages) == 2

def test_b(manager_with_messages):
    stats = manager_with_messages.get_conversation_summary()
    assert stats["total_messages"] == 2
```

---

## Debugging тестов

### Запуск с отладкой

```bash
# Остановка на первой ошибке
pytest -x

# Вывод print statements
pytest -s

# Детальный вывод
pytest -vv

# Отладчик на ошибках
pytest --pdb

# Trace выполнения
pytest --trace
```

---

### Pytest выводит много информации

```python
# Использовать capsys для проверки вывода
def test_display_welcome(console_app, capsys):
    """Тест приветственного сообщения."""
    console_app.display_welcome()
    
    captured = capsys.readouterr()
    assert "LLM-Ассистент" in captured.out
```

---

## Примеры тестов из проекта

### test_dialog_manager.py

```python
def test_add_user_message():
    """Тест добавления сообщения пользователя."""
    manager = DialogManager(max_history=10)
    
    manager.add_user_message("Hello, world!")
    
    assert len(manager) == 1
    history = manager.get_history()
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello, world!"
```

---

### test_llm_client.py

```python
@pytest.mark.asyncio
async def test_get_response_with_retry(llm_client, mocker):
    """Тест retry логики при Rate Limit."""
    from openai import RateLimitError
    
    # Первые 2 вызова — ошибка, 3-й — успех
    mock_responses = [
        RateLimitError("Rate limit", response=None, body=None),
        RateLimitError("Rate limit", response=None, body=None),
        Mock(choices=[Mock(message=Mock(content="Success"))]),
    ]
    
    mock_create = mocker.patch.object(
        llm_client.client.chat.completions,
        "create",
        side_effect=mock_responses
    )
    
    response = await llm_client.get_response("Test", "Prompt", [])
    
    assert response == "Success"
    assert mock_create.call_count == 3
```

---

### test_console.py

```python
def test_stats_command(console_app, capsys):
    """Тест команды /stats."""
    # Добавить сообщения
    console_app.dialog_manager.add_user_message("Test 1")
    console_app.dialog_manager.add_assistant_message("Response 1")
    console_app.dialog_manager.add_user_message("Test 2")
    console_app.dialog_manager.add_assistant_message("Response 2")
    
    # Выполнить команду
    is_exit = console_app._handle_command("/stats")
    
    # Проверить вывод
    captured = capsys.readouterr()
    assert "Всего сообщений: 4" in captured.out
    assert "Ваших сообщений: 2" in captured.out
    assert "Ответов ассистента: 2" in captured.out
    assert is_exit is False
```

---

## Continuous Integration (будущее)

### GitHub Actions pipeline (пример)

```yaml
name: Quality Checks

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install uv
      run: pip install uv
    
    - name: Install dependencies
      run: |
        uv venv
        uv pip install -e ".[dev]"
    
    - name: Run quality checks
      run: make quality
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

---

## 📊 Статистика проекта

**Текущее состояние:**
- ✅ **149 тестов** (100% проходят)
- ✅ **87.59% coverage** (цель превышена)
- ✅ **0 ошибок Ruff**
- ✅ **0 ошибок Mypy** (strict mode)
- ✅ **11 модулей** (100% типизированы)

---

## 📚 Следующие шаги

- **[Development Workflow](07_development_workflow.md)** — TDD процесс разработки
- **[Визуализация проекта](09_project_visualizations.md)** — диаграммы и схемы
- **[Codebase Tour](03_codebase_tour.md)** — обзор всех модулей

---

**⏱️ Время изучения:** 30 минут  
**🎯 Следующий гайд:** [Визуализация проекта →](09_project_visualizations.md)

