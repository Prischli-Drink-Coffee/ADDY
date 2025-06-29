#!/bin/bash

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${PROJECT_ROOT}/.env"
export PYTHONPATH="${PROJECT_ROOT}/src:$PYTHONPATH"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${PROJECT_ROOT}/.venv/lib/python3.9/site-packages/torch/lib"
cd "$PROJECT_ROOT"
source ./src/scripts/check_env.sh

if ! check_env_file .env DB_HOST DB_PORT DB_USER DB_PASSWORD DB SERVER_HOST SERVER_PORT DEBUG ACCESS_TOKEN_EXPIRE_MINUTES REFRESH_TOKEN_EXPIRE_DAYS; then
    exit 1
fi

echo "Все переменные окружения установлены корректно"

./.venv/bin/python -m src.utils.create_sql