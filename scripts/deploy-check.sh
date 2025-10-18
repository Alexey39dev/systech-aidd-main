#!/bin/bash

# =============================================================================
# СКРИПТ ПРОВЕРКИ ГОТОВНОСТИ К ДЕПЛОЮ SYSTECH-AIDD
# =============================================================================
# Этот скрипт проверяет готовность к развертыванию на production сервере
# 89.223.67.136
#
# Использование: ./scripts/deploy-check.sh
# =============================================================================

set -e  # Остановка при любой ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Счетчики
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# Функция для вывода заголовка
print_header() {
    echo -e "\n${BLUE}=============================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}=============================================================================${NC}"
}

# Функция для проверки
check() {
    local description="$1"
    local command="$2"
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    echo -n "Проверка: $description... "
    
    if eval "$command" >/dev/null 2>&1; then
        echo -e "${GREEN}✓ ПРОЙДЕНО${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        return 0
    else
        echo -e "${RED}✗ ОШИБКА${NC}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        return 1
    fi
}

# Функция для предупреждения
warning() {
    local message="$1"
    echo -e "${YELLOW}⚠️  ПРЕДУПРЕЖДЕНИЕ: $message${NC}"
}

# Функция для ошибки
error() {
    local message="$1"
    echo -e "${RED}❌ ОШИБКА: $message${NC}"
}

# Функция для информации
info() {
    local message="$1"
    echo -e "${BLUE}ℹ️  $message${NC}"
}

# =============================================================================
# НАЧАЛО ПРОВЕРКИ
# =============================================================================

print_header "ПРОВЕРКА ГОТОВНОСТИ К ДЕПЛОЮ SYSTECH-AIDD"

echo -e "${BLUE}Сервер: 89.223.67.136${NC}"
echo -e "${BLUE}Пользователь: systech${NC}"
echo -e "${BLUE}Рабочая директория: /opt/systech/dolgachev${NC}"
echo -e "${BLUE}Порты: API 8002, Frontend 3002${NC}"

# =============================================================================
# ПРОВЕРКА ЛОКАЛЬНЫХ ФАЙЛОВ
# =============================================================================

print_header "ПРОВЕРКА ЛОКАЛЬНЫХ ФАЙЛОВ"

# Проверка SSH ключа
SSH_KEY_PATH=""
if [ -f "systech_admin_key" ]; then
    SSH_KEY_PATH="systech_admin_key"
elif [ -f "C:/Users/a.dolgachev/Downloads/systech_admin_key" ]; then
    SSH_KEY_PATH="C:/Users/a.dolgachev/Downloads/systech_admin_key"
else
    error "SSH ключ systech_admin_key не найден!"
    echo "  Скопируйте ключ из C:/Users/a.dolgachev/Downloads/systech_admin_key в текущую директорию"
    exit 1
fi

check "SSH ключ найден" "test -f '$SSH_KEY_PATH'"

# Проверка файлов конфигурации
check "Файл docker-compose.prod.yml существует" "test -f docker-compose.prod.yml"
check "Файл env.production.template существует" "test -f env.production.template"

# Проверка .env файла
if [ -f ".env" ]; then
    check "Файл .env существует" "test -f .env"
    
    # Проверка обязательных переменных в .env
    if grep -q "OPENROUTER_API_KEY=" .env && ! grep -q "OPENROUTER_API_KEY=ЗАПОЛНИТЬ" .env; then
        check "OPENROUTER_API_KEY заполнен в .env" "grep -q 'OPENROUTER_API_KEY=' .env"
    else
        warning "OPENROUTER_API_KEY не заполнен в .env"
    fi
    
    if grep -q "DATABASE_URL=" .env && ! grep -q "ЗАПОЛНИТЬ_ПАРОЛЬ_БД" .env; then
        check "DATABASE_URL заполнен в .env" "grep -q 'DATABASE_URL=' .env"
    else
        warning "DATABASE_URL не заполнен в .env"
    fi
else
    warning "Файл .env не найден. Создайте его на основе env.production.template"
fi

# Проверка директории prompts
check "Директория prompts существует" "test -d prompts"
check "Файл prompts/default.txt существует" "test -f prompts/default.txt"

# =============================================================================
# ПРОВЕРКА SSH ПОДКЛЮЧЕНИЯ
# =============================================================================

print_header "ПРОВЕРКА SSH ПОДКЛЮЧЕНИЯ"

# Проверка SSH подключения
if check "SSH подключение к серверу" "ssh -i '$SSH_KEY_PATH' -o ConnectTimeout=10 -o BatchMode=yes systech@89.223.67.136 'echo connected'"; then
    info "SSH подключение работает"
else
    error "Не удается подключиться к серверу по SSH"
    echo "  Проверьте:"
    echo "  - Правильность IP адреса сервера"
    echo "  - Наличие SSH ключа systech_admin_key"
    echo "  - Доступность сервера в сети"
    echo "  - Правильность имени пользователя systech"
    exit 1
fi

# =============================================================================
# ПРОВЕРКА СЕРВЕРА
# =============================================================================

print_header "ПРОВЕРКА СЕРВЕРА"

# Проверка Docker
check "Docker установлен на сервере" "ssh -i '$SSH_KEY_PATH' systech@89.223.67.136 'docker --version'"
check "Docker Compose установлен на сервере" "ssh -i '$SSH_KEY_PATH' systech@89.223.67.136 'docker compose version'"

# Проверка свободности портов
check "Порт 8002 свободен на сервере" "ssh -i '$SSH_KEY_PATH' systech@89.223.67.136 '! netstat -tuln | grep :8002'"
check "Порт 3002 свободен на сервере" "ssh -i '$SSH_KEY_PATH' systech@89.223.67.136 '! netstat -tuln | grep :3002'"

# Проверка прав на создание директории
check "Права на создание /opt/systech/dolgachev" "ssh -i '$SSH_KEY_PATH' systech@89.223.67.136 'mkdir -p /opt/systech/dolgachev && echo test > /opt/systech/dolgachev/test.txt && rm /opt/systech/dolgachev/test.txt'"

# Проверка доступности GitHub Container Registry
check "Доступность ghcr.io с сервера" "ssh -i '$SSH_KEY_PATH' systech@89.223.67.136 'curl -s --connect-timeout 10 https://ghcr.io'"

# =============================================================================
# ПРОВЕРКА DOCKER ОБРАЗОВ
# =============================================================================

print_header "ПРОВЕРКА DOCKER ОБРАЗОВ"

# Проверка доступности образов
check "Образ bot:latest доступен" "ssh -i '$SSH_KEY_PATH' systech@89.223.67.136 'docker pull ghcr.io/dolgachev/bot:latest'"
check "Образ api:latest доступен" "ssh -i '$SSH_KEY_PATH' systech@89.223.67.136 'docker pull ghcr.io/dolgachev/api:latest'"
check "Образ frontend:latest доступен" "ssh -i '$SSH_KEY_PATH' systech@89.223.67.136 'docker pull ghcr.io/dolgachev/frontend:latest'"

# =============================================================================
# ИТОГОВЫЙ ОТЧЕТ
# =============================================================================

print_header "ИТОГОВЫЙ ОТЧЕТ"

echo -e "${BLUE}Всего проверок: $TOTAL_CHECKS${NC}"
echo -e "${GREEN}Пройдено: $PASSED_CHECKS${NC}"
echo -e "${RED}Ошибок: $FAILED_CHECKS${NC}"

if [ $FAILED_CHECKS -eq 0 ]; then
    echo -e "\n${GREEN}🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!${NC}"
    echo -e "${GREEN}Сервер готов к развертыванию.${NC}"
    echo -e "\n${BLUE}Следующие шаги:${NC}"
    echo -e "1. Скопируйте файлы на сервер:"
    echo -e "   scp -i '$SSH_KEY_PATH' docker-compose.prod.yml systech@89.223.67.136:/opt/systech/dolgachev/"
    echo -e "   scp -i '$SSH_KEY_PATH' .env systech@89.223.67.136:/opt/systech/dolgachev/"
    echo -e "   scp -r -i '$SSH_KEY_PATH' prompts/ systech@89.223.67.136:/opt/systech/dolgachev/"
    echo -e "\n2. Подключитесь к серверу и запустите сервисы:"
    echo -e "   ssh -i '$SSH_KEY_PATH' systech@89.223.67.136"
    echo -e "   cd /opt/systech/dolgachev"
    echo -e "   docker compose -f docker-compose.prod.yml up -d"
    exit 0
else
    echo -e "\n${RED}❌ ОБНАРУЖЕНЫ ОШИБКИ!${NC}"
    echo -e "${RED}Исправьте ошибки перед развертыванием.${NC}"
    exit 1
fi