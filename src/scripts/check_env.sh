#!/bin/bash

# Функция для проверки .env файла
check_env_file() {
    local env_file="${1:-.env}"
    local required_vars=("${@:2}")

    # Проверяем существование файла
    if [ ! -f "${env_file}" ]; then
        echo "Error: .env file not found at ${env_file}" >&2
        return 1
    fi

    # Проверяем наличие обязательных переменных в файле
    local missing_in_file=()
    for var in "${required_vars[@]}"; do
        if ! grep -qE "^${var}=" "${env_file}"; then
            missing_in_file+=("${var}")
        fi
    done

    if [ ${#missing_in_file[@]} -gt 0 ]; then
        echo "Error: Missing required variables in .env file:" >&2
        for missing_var in "${missing_in_file[@]}"; do
            echo "  - ${missing_var}" >&2
        done
        return 1
    fi

    # Загружаем файл
    set -a
    source "${env_file}" || return 1
    set +a

    # Проверяем, что переменные установлены
    local unset_vars=()
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            unset_vars+=("${var}")
        fi
    done

    if [ ${#unset_vars[@]} -gt 0 ]; then
        echo "Error: Required variables are not set after loading .env:" >&2
        for unset_var in "${unset_vars[@]}"; do
            echo "  - ${unset_var}" >&2
        done
        return 1
    fi

    return 0
}

# Если скрипт вызван напрямую, а не через source
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Пример использования:
    # check_env.sh /path/to/.env DB_HOST DB_PORT DB_USER DB_PASSWORD DB SERVER_HOST SERVER_PORT DEBUG ACCESS_TOKEN_EXPIRE_MINUTES REFRESH_TOKEN_EXPIRE_DAYS
    check_env_file "$@"
    exit $?
fi