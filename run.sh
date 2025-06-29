#!/bin/bash

set -e

echo "--- Running FrameReader Backend ---"

IMAGE_NAME="addy-backend:latest"
ENV_FILE="${PROJECT_ROOT}/.env"
source ./src/scripts/check_env.sh

echo "Running Docker container for backend..."
docker run --rm -it \
  -p 8005:8005 \
  --name addy-backend-app \
  $ENV_VARS \
  $IMAGE_NAME

echo "--- Backend Container Stopped ---"