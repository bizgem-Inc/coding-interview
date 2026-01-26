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

# コマンドを実行
exec "$@"
