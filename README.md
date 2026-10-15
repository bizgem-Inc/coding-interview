# coding-interview

## Category API

認証不要で Category の CRUD を提供します。

| Method | URL | 動作 |
| --- | --- | --- |
| GET | `/api/categories/` | 一覧取得 |
| POST | `/api/categories/` | 作成 |
| GET | `/api/categories/{id}/` | 詳細取得 |
| PUT | `/api/categories/{id}/` | 更新（`company`、`name` は必須） |
| PATCH | `/api/categories/{id}/` | 部分更新 |
| DELETE | `/api/categories/{id}/` | 削除 |

作成リクエスト例:

```json
{
  "company": "<既存の Company の UUID>",
  "name": "食品",
  "parent_category": null
}
```

- `company`、`name` は必須です。名前は空白のみを不可とし、前後の空白を除去して最大255文字まで受け付けます。同一企業内の名前重複は不可です。
- `parent_category` は省略・null を許可します。指定する場合は既存の Category の UUID が必要です。
- 階層の整合性を保つため、親子は同じ企業に所属し、自己参照・循環参照を禁止する前提としています。企業の変更でも既存の親子関係を検証します。
- `id`、`created_at`、`updated_at` は自動生成される読み取り専用項目です。
- 入力エラーは400、存在しない・不正な形式の詳細IDは404を返します。作成は201、取得・更新は200、削除は204を返します。
- 親カテゴリの削除時は、既存モデルの `SET_NULL` に従い子カテゴリを保持します。

## テスト

既存の Pipfile / Pipfile.lock に従って依存関係をインストールし、PostgreSQL を起動して実行してください。接続先は `config/settings.py` の既存環境変数（`POSTGRES_DB`、`POSTGRES_USER`、`POSTGRES_PASSWORD`、`DB_HOST_NAME`、`DB_PORT`）で指定できます。テスト実行ユーザーにはテストDBの作成権限が必要です。

```sh
pipenv sync
pipenv run python manage.py test api.tests
```

CRUD の正常系、PUT / PATCH、必須・文字数・外部キー検証、企業内の一意性、親子関係、読み取り専用項目、404、削除時の子カテゴリ保持を検証します。
