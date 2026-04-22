# Python 3.11の軽量イメージを使用
FROM python:3.11-slim

# OSの依存パッケージをインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリの設定
WORKDIR /app

# 依存パッケージのインストール
# pipenvを使用しつつ、psycopg2-binaryを明示的にインストールしてビルドを安定させる
RUN pip install --no-cache-dir pipenv psycopg2-binary

COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --skip-lock

# ソースコードのコピー
COPY . .

# サーバー起動 (開発用)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
