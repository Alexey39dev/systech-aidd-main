# Скрипт запуска Telegram-бота через uv
# Очищает проблемные переменные окружения Python

Write-Host "Запуск Telegram-бота..." -ForegroundColor Green

# Очистка проблемных переменных окружения
Remove-Item Env:\PYTHONHOME -ErrorAction SilentlyContinue
Remove-Item Env:\PYTHONPATH -ErrorAction SilentlyContinue

# Запуск бота
.\.venv\Scripts\python.exe -m src.main

