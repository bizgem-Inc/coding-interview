# Coding Interview Project

## 概要
このプロジェクトは、カテゴリ管理システムのAPIを提供するDjangoアプリケーションです。

## 技術スタック
- Python 3.11
- Django
- Django REST framework
- PostgreSQL

## セットアップ手順

### 1. 環境構築
```bash
# Python 3.11のインストール
brew install python@3.11

# PostgreSQLのインストール
brew install postgresql@14
brew services start postgresql@14

# データベースの作成
createdb -U postgres coding_test
```

### 2. プロジェクトのセットアップ
```bash
# 依存関係のインストール
pipenv install

# 仮想環境のアクティベート
pipenv shell

# マイグレーションの実行
python manage.py migrate

# 開発サーバーの起動
python manage.py runserver
```

## APIエンドポイント

### カテゴリ管理

#### カテゴリ一覧の取得
```bash
curl http://localhost:8000/api/categories/
```

#### カテゴリの作成
```bash
curl -X POST http://localhost:8000/api/categories/ \
  -H "Content-Type: application/json" \
  -d '{
    "company": "ae8f0da0-231c-4ba3-b14f-ab4642d7e589",
    "name": "カテゴリ名",
    "parent_category": null
  }'
```

#### カテゴリの詳細取得
```bash
curl http://localhost:8000/api/categories/{category_id}/
```

#### カテゴリの更新
```bash
curl -X PUT http://localhost:8000/api/categories/{category_id}/ \
  -H "Content-Type: application/json" \
  -d '{
    "company": "ae8f0da0-231c-4ba3-b14f-ab4642d7e589",
    "name": "更新されたカテゴリ名",
    "parent_category": null
  }'
```

#### カテゴリの削除
```bash
curl -X DELETE http://localhost:8000/api/categories/{category_id}/
```

## テストの実行
```bash
python manage.py test api.tests.test_views.CategoryViewSetTests
```

## データベース接続情報
- ホスト: localhost
- ポート: 5432
- データベース: coding_test
- ユーザー: postgres
- パスワード: password