#!/bin/bash

# データベースの準備ができるまで待機
echo "Waiting for PostgreSQL..."

while ! nc -z $DB_HOST_NAME $DB_PORT; do
  sleep 0.1
done

echo "PostgreSQL started"

# マイグレーションを実行
echo "Running migrations..."
python manage.py migrate --noinput

# DEBUGがTrueの場合、debugpyを有効にする
if [ "$DEBUG" = "True" ] || [ "$DEBUG" = "true" ]; then
    echo "DEBUG mode enabled. Starting with debugpy..."
    # debugpyでDjangoを起動（リモートデバッグ用）
    # $@から'python'を除いて残りの引数を渡す
    shift
    exec python -m debugpy --listen 0.0.0.0:5678 --wait-for-client "$@"
else
    # 通常モード
    exec "$@"
fi
