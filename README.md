# coding-interview

## tasks

- Category モデルの読み取り・作成・更新・削除が出来る API
  ※ views/category.py, serializers/category.py に実装するイメージ
- API のテストの実装
  ※ test_views.py に実装するイメージ

# 環境の初期化

## 前提条件

- pipenv が使用できる状態であること
- docker が使用できる状態であること

## 環境構築

1. 依存関係のインストール
   必要な Python パッケージをインストール

   ```bash
   pipenv install
   ```

2. データベースのセットアップ
   Docker を使用して PostgreSQL コンテナを起動

   ```bash
   docker-compose -f container/compose.yaml up -d
   ```

3. マイグレーションの適用\
   Django のマイグレーションを適用してデータベースを初期化

   ```bash
   pipenv run python manage.py migrate
   ```

# 実行方法

## 起動

```bash
pipenv run python manage.py runserver
```

## ユニットテスト

```bash
pipenv run python manage.py test
```

# エンドポイント一覧

ベース URL:`http://127.0.0.1:8000/api/`

| メソッド | URL パターン        | 説明                     |
| -------- | ------------------- | ------------------------ |
| GET      | `/categories/`      | カテゴリ一覧を取得       |
| POST     | `/categories/`      | 新しいカテゴリを作成     |
| GET      | `/categories/{id}/` | 特定のカテゴリを取得     |
| PUT      | `/categories/{id}/` | 特定のカテゴリを更新     |
| PATCH    | `/categories/{id}/` | 特定のカテゴリを部分更新 |
| DELETE   | `/categories/{id}/` | 特定のカテゴリを削除     |

## サンプルリクエスト

### GET：カテゴリ一覧を取得

```bash
curl -X GET http://127.0.0.1:8000/api/categories/
```

### POST：新しいカテゴリを作成

`company`は前に準備が必要

```bash
curl -X POST http://127.0.0.1:8000/api/categories/ \
  -H "Content-Type: application/json" \
  -d '{
    "company": "F8653416-A15B-4ABC-9CB4-7AA6DA39B757",
    "name": "New Category Name"
  }'
```

### GET：特定のカテゴリを取得

```bash
curl -X GET http://127.0.0.1:8000/api/categories/a49f639f-69ae-4dff-bf1a-8152d15df44c/
```

### PUT：特定のカテゴリを更新

`company`は事前に準備が必要

```bash
curl -X PUT http://127.0.0.1:8000/api/categories/a49f639f-69ae-4dff-bf1a-8152d15df44c/ \
  -H "Content-Type: application/json" \
  -d '{
    "company": "F8653416-A15B-4ABC-9CB4-7AA6DA39B757",
    "name": "Update Category name"
  }'
```

### PATCH：特定のカテゴリを部分更新

```bash
curl -X PATCH http://127.0.0.1:8000/api/categories/a49f639f-69ae-4dff-bf1a-8152d15df44c/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Partial update name"
  }'
```

### DELETE：特定のカテゴリを削除

カテゴリ ID: `a49f639f-69ae-4dff-bf1a-8152d15df44c`

```bash
curl -X DELETE http://127.0.0.1:8000/api/categories/a49f639f-69ae-4dff-bf1a-8152d15df44c/
```
