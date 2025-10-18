# DevOps Roadmap

## Обзор

MVP DevOps roadmap для проекта systech-aidd. Цель: пройти путь от локального отдельного запуска до удаленного сервера с автоматическим развертыванием максимально быстро.

## Спринты

| Код | Описание | Статус |
|-----|----------|--------|
| D0 | Basic Docker Setup | ✅ Completed |
| D1 | Build & Publish | ✅ Completed |
| D2 | Развертывание на сервер | ✅ Completed |
| D3 | Auto Deploy | ⏳ Ожидает |

## D0: Basic Docker Setup

**Статус:** ✅ **Completed** (18 октября 2025)

**Цели:**
- Запустить все сервисы локально через docker-compose одной командой
- Создать базовую Docker инфраструктуру для всех компонентов проекта

**Описание состава работ:**
- Создать простые Dockerfile для bot, api, frontend
- Создать docker-compose.yml с 4 сервисами: PostgreSQL, Bot, API, Frontend
- Создать базовый .dockerignore для каждого сервиса
- Проверить: `docker-compose up` - всё работает локально
- Учесть наличие docker-compose.yml для PostgreSQL, .env файла в проекте

**Реализовано:**
- ✅ 3 Dockerfile (bot, api, frontend) с single-stage подходом
- ✅ docker-compose.yml с 4 сервисами + миграции
- ✅ .dockerignore файлы для оптимизации build context
- ✅ .env.example с шаблоном переменных окружения
- ✅ Bot адаптирован для работы в Docker (без интерактивного ввода)
- ✅ Все сервисы работают стабильно: `docker-compose up -d`

**План реализации:** [План спринта](plans/d0-basic-docker-setup.md)  
**Отчет о тестировании:** [Отчет о тестировании](../reports/d0-testing-report.md)  
**Итоговый отчет:** [Итоговый отчет](../reports/d0-summary.md)

## D1: Build & Publish

**Статус:** ✅ **Completed** (18 октября 2025)

**Реализовано:**
- ✅ GitHub Actions workflow для автоматической сборки
- ✅ Matrix strategy для параллельной сборки 3 образов
- ✅ Публикация в GitHub Container Registry (ghcr.io)
- ✅ Публичный доступ к образам (без авторизации)
- ✅ Docker layer caching для ускорения сборки
- ✅ docker-compose.prod.yml для использования registry образов
- ✅ Badge статуса сборки в README
- ✅ Документация по GitHub Actions

**План реализации:** [d1-build-publish.md](plans/d1-build-publish.md)  
**Отчет о тестировании:** [d1-testing-report.md](reports/d1-testing-report.md)  
**Отчет о проверке:** [d1-verification.md](reports/d1-verification.md)  
**Итоговый отчет:** [d1-summary.md](reports/d1-summary.md)

## D2: Развертывание на сервер

**Статус:** ✅ **Completed** (18 октября 2025)

**Цели:**
- Развернуть приложение на удаленном сервере вручную (пошаговая инструкция)
- Создать процесс ручного деплоя для быстрого тестирования

**Реализовано:**
- ✅ Создана детальная инструкция `docs/guides/manual-deploy.md`
- ✅ Создан шаблон `.env.production` с описанием всех переменных
- ✅ Обновлен `docker-compose.prod.yml` для production развертывания
- ✅ Исправлены проблемы с `.gitignore` и `Dockerfile.frontend`
- ✅ Все сервисы развернуты на сервере 89.223.67.136
- ✅ API доступен по http://89.223.67.136:8002
- ✅ Frontend доступен по http://89.223.67.136:3002
- ✅ Bot работает в консольном режиме
- ✅ База данных инициализирована с миграциями

**План реализации:** [d2-manual-deploy.md](plans/d2-manual-deploy.md)  
**Итоговый отчет:** [d2-summary.md](reports/d2-summary.md)

## D3: Auto Deploy

**Цели:**
- Автоматическое развертывание на сервер через GitHub Actions по кнопке
- Создать полноценный CI/CD pipeline с автоматическим деплоем

**Описание состава работ:**
- Создать GitHub Actions workflow `.github/workflows/deploy.yml`
- Trigger: ручной запуск (workflow_dispatch)
- SSH подключение к серверу с помощью SSH ключа
- Pull новых версий образов
- Restart сервисов через docker-compose
- Создать инструкцию по настройке secrets (SSH_KEY, HOST, USER в GitHub Actions)
- Добавить уведомления о статусе деплоя

**План реализации:** [Будет создан после выполнения спринта](plans/)

## Статусы

- 🚧 **Планируется** - Спринт готов к выполнению
- ⏳ **Ожидает** - Спринт ожидает завершения предыдущих
- ✅ **Завершен** - Спринт выполнен
- ❌ **Отменен** - Спринт отменен

## Примечания

- Все спринты выполняются в режиме Plan Mode для детального планирования
- После выполнения каждого спринта создается план реализации в директории `devops/doc/plans/`
- Фокус на простоте и скорости реализации (MVP подход)
- Избегаем преждевременной оптимизации
