# カテゴリー管理API

Django REST Frameworkを使用したカテゴリー管理APIです。企業とカテゴリーの階層構造を管理することができます。

## 必要条件

- Python 3.11
- PostgreSQL
- Docker & Docker Compose (オプション)

## ローカル環境でのインストールと実行

### 方法1: Dockerを使用する場合 (推奨)

1. **Dockerコンテナの起動**
   ```bash
   docker compose up --build
   ```

2. **マイグレーションの実行とFixturesをロードする**
   ```bash
   docker compose exec server python manage.py migrate
   docker compose exec server python manage.py loaddata companies categories
   ```

3. **動作確認**
   - APIサーバー: http://localhost:8000
   - データベース: localhost:5432

### 方法2: ローカル環境で直接実行する場合

1. **Pipenvのインストール**
   ```bash
   pip install pipenv
   ```

2. **依存関係のインストール**
   ```bash
   pipenv install --dev
   ```

3. **仮想環境の有効化**
   ```bash
   pipenv shell
   ```

4. **環境変数の設定**
   ```bash
   export POSTGRES_DB=coding-test
   export POSTGRES_USER=root
   export POSTGRES_PASSWORD=password
   export DB_HOST_NAME=localhost
   export DEBUG=1
   ```

5. **マイグレーションの実行**
   ```bash
   python manage.py migrate
   ```

6. **Fixturesをロードする**
   ```bash
   python manage.py loaddata companies categories
   ```

8. **開発サーバーの起動**
   ```bash
   python manage.py runserver
   ```

9. **動作確認**
   - APIサーバー: http://localhost:8000

## API エンドポイント

### カテゴリー管理

- `GET /api/categories/` - カテゴリー一覧取得
- `POST /api/categories/` - 新規カテゴリー作成
- `GET /api/categories/{id}/` - カテゴリー詳細取得
- `PATCH /api/categories/{id}/` - カテゴリー更新
- `DELETE /api/categories/{id}/` - カテゴリー削除

### クエリパラメータ
- `company_id` - 企業IDでフィルタリング

細かいは http://localhost:8000/api/categories/ の OPTIONSで確認できます

### リクエスト/レスポンス例

**カテゴリー作成**
```bash
POST /api/categories/
Content-Type: application/json

{
  "name": "テストカテゴリー",
  "company": 1,
  "parent_category": null
}
```

**カテゴリー一覧取得 (企業フィルタリング)**
```bash
GET /api/categories/?company_id=1
```

## テストの実行

```bash
# Dockerを使用する場合
docker compose exec server python manage.py test

# ローカル環境の場合
pipenv run python manage.py test
```

## プロジェクト構造

```
coding-interview/
├── api/                    # メインアプリケーション
│   ├── models/            # データモデル
│   ├── serializers/       # APIシリアライザー
│   ├── views/            # APIビュー
│   └── tests/            # テストファイル
├── config/                # Django設定
├── Dockerfile             # Dockerイメージ定義
├── docker-compose.yml     # Docker Compose設定
├── Pipfile               # Python依存関係
└── manage.py             # Django管理スクリプト
```