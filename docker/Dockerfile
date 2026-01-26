# ベースイメージとしてPython 3.11を使用
FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# Pythonの出力をバッファリングしない設定
ENV PYTHONUNBUFFERED=1

# システムの依存関係をインストール（PostgreSQL クライアント用）
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# requirements.txtをコピーして依存関係をインストール
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# ポート8000を公開
EXPOSE 8000

# エントリーポイントスクリプトを実行可能にする
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# エントリーポイントとコマンドを設定
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
