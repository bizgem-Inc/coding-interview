# syntax=docker/dockerfile:1
FROM python:3.11

# 環境変数：Python の出力をバッファしない
ENV PYTHONUNBUFFERED=1

# pipenv をインストール
RUN pip install --no-cache-dir pipenv

# 作業ディレクトリ作成
WORKDIR /code

# Pipfile, Pipfile.lock をコピー
COPY Pipfile Pipfile.lock ./

# 依存パッケージをインストール（バージョン固定）
RUN pipenv install --deploy --ignore-pipfile

# アプリケーションコードをすべてコピー
COPY . .

# ポート開放（開発用）
EXPOSE 8000

# デフォルトの起動コマンド（docker-compose.yml の `command` が優先される）
CMD ["pipenv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]