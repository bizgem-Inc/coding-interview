FROM python:3.11-slim

# 環境変数を設定
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 作業ディレクトリを設定
WORKDIR /app

# システム依存関係をインストール
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    netcat-traditional \
    postgresql \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係をインストール
COPY Pipfile Pipfile.lock ./
RUN pip install --upgrade pip
RUN pip install pipenv && pipenv install --system --dev

# プロジェクトをコピー
COPY . /app/

# 非rootユーザーを作成
RUN useradd -m -u 1000 django && chown -R django:django /app
USER django

# 静的ファイルを収集してアプリケーションを実行(django-admin, swaggerに必要)
RUN python manage.py collectstatic --noinput
CMD ["uvicorn", "config.asgi:application", "--host", "0.0.0.0", "--port", "8000"]