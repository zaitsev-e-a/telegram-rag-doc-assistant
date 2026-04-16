#!/usr/bin/env bash
set -e

echo "Запуск Redis..."
redis-server --daemonize yes

echo "Запуск Qdrant..."
/usr/local/bin/qdrant &

echo "Запуск HTTP health server..."
uvicorn web_app:app --host 0.0.0.0 --port 7860 &

echo "Ожидание запуска сервисов..."
sleep 5

echo "Запуск Telegram-бота..."
python main.py