# coding-interview

## 概要

Django と PostgreSQL を使用した Web アプリケーション

## 必要な環境

- Docker
- Docker Compose

## セットアップ方法

### 1. 環境変数の設定

```bash
# 環境変数ファイルをコピー
cp .env.example .env

# 必要に応じて.envファイルを編集
# デフォルト設定で動作します
```

### 2. 依存関係のインストール（Pipfile.lock の生成）

```bash
# pipenvがインストールされていない場合
pip install pipenv

# Pipfile.lockを生成
pipenv lock

# パッケージを追加する場合上記のPipfileに追加した上でpipenv lockを実行してください
```

### 3. Docker Compose で起動

```bash
# ビルドして起動
docker compose up --build

# バックグラウンドで起動する場合
docker compose up -d --build
```

### 4. アプリケーションへのアクセス

- Web アプリケーション: http://localhost:8000

## 開発時の操作

### コンテナの停止

```bash
docker compose down
```

### データベースも含めて完全に削除

```bash
docker compose down -v
```

### Django コマンドの実行

```bash
# マイグレーションの作成
docker compose exec web python manage.py makemigrations

# マイグレーションの適用
docker compose exec web python manage.py migrate

# スーパーユーザーの作成(django adminのログインに必要です)
docker compose exec web python manage.py createsuperuser

# Djangoシェル
docker compose exec web python manage.py shell

# データベースへの接続
docker compose exec web python manage.py dbshell
```

### ruff コマンドの実行

```bash
docker compose exec web python -m ruff format .
```

1. ruff の実行方法: `python -m ruff`を使用
2. フォーマット: `python -m ruff format .`
3. リントチェック: `python -m ruff check .`
4. 自動修正付きリント: `python -m ruff check . --fix`

### dbdoc の更新

```bash
# マイグレーション済みの状態が前提です
rm -r dbdoc
docker run --rm --network coding-interview_default \
  -v $PWD:/work -w /work \
  ghcr.io/k1low/tbls doc \
  "postgres://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-postgres}@db:5432/${POSTGRES_DB:-interview_db}?sslmode=disable"
```
