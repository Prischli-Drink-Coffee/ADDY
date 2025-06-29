#!/bin/bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${PROJECT_ROOT}/.env"
source ./src/scripts/check_env.sh

echo "--- Building ADDY Backend ---"

if [ -f "${PROJECT_ROOT}/db.sh" ]; then
    echo "Initializing database..."
    bash "${PROJECT_ROOT}/db.sh"
fi

echo "Building Docker image..."
docker build -t addy-backend:latest -f "${PROJECT_ROOT}/docker/Dockerfile" "$PROJECT_ROOT"

echo "--- Build Complete ---"