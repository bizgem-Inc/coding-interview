# coding-interview

## セットアップ

### 前提条件

- Python 3.11
- uv
- PostgreSQL 15
- Docker, Docker Compose（Docker 環境で実行する場合）

### ローカル環境

```bash
# 1. 依存関係のインストール
uv sync

# 2. 環境変数の設定
cp .env.example .env
# .env を編集してDB接続情報を設定

# 3. マイグレーション
uv run python manage.py migrate

# 4. サーバー起動
uv run python manage.py runserver
```

### Docker Compose

```bash
# 1. サービスの起動（DBとWeb）
docker compose up -d

# 2. マイグレーション
docker compose exec web python manage.py migrate

# 3. 停止
docker compose down
```

## テスト実行

### 全テスト（Djangoテストランナー）

Domain単体、Application単体、Repository結合、Web統合テストを実行します。

```bash
uv run python manage.py test
```

### E2Eテスト

実際のHTTPサーバー（live_server）に対するエンドツーエンドテストを実行します。

```bash
uv run pytest api/tests/e2e/
```

### 型検査

```bash
uv run --with pyright pyright
```

## 環境変数

`.env.example` を参照してください。

| 変数 | デフォルト | 説明 |
|------|-----------|------|
| `POSTGRES_DB` | `coding-test` | データベース名 |
| `POSTGRES_USER` | `root` | ユーザー名 |
| `POSTGRES_PASSWORD` | `password` | パスワード |
| `DB_HOST_NAME` | `localhost` | DBホスト |
| `DB_PORT` | `5432` | DBポート |
