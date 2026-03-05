# coding-interview

## Category CRUD API

### エンドポイント
- **GET** `/api/categories/` : 一覧
- **POST** `/api/categories/` : 作成
- **GET** `/api/categories/{id}/` : 詳細
- **PUT** `/api/categories/{id}/` : 更新
- **PATCH** `/api/categories/{id}/` : 部分更新
- **DELETE** `/api/categories/{id}/` : 削除

## テストの実行方法

このリポジトリの通常設定（`config/settings.py`）は **PostgreSQL** を使用します。
一方で、採用側の実行環境（CI等）ではDBが起動していない可能性があるため、**テストをDB不要で安定して実行できるように**、
テスト専用設定として **SQLite** を使用する `config/settings_test.py` を用意しています。

### SQLite（推奨: DB不要で実行）

```bash
python manage.py test --settings=config.settings_test
```

### PostgreSQL（通常設定で実行）

```bash
python manage.py test --settings=config.settings
```

※ PostgreSQLでのテスト実行は、PostgreSQLの起動・接続設定・テストDB作成権限（CREATEDB）等が必要になります。