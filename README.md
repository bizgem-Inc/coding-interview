# Category CRUD API

Django REST Frameworkを使用し、`Category`モデルの一覧取得、詳細取得、作成、更新、削除を行うAPIを実装しました。

認証は課題要件に従って実装していません。入力値の検証に加え、同時リクエストによるデータベース制約違反やカテゴリ階層の不整合もAPIエラーとして処理します。

## 実装内容

- `ModelSerializer`によるCategoryデータの入出力とバリデーション
- `ModelViewSet`によるCRUD API
- `DefaultRouter`によるURL登録
- Company・CategoryモデルのDjangoアプリへの明示的な登録
- Company・Categoryテーブルを作成する初期migration
- 正常系、異常系、同時リクエストを含むAPIテスト

## API

| Method | Endpoint | 説明 |
| --- | --- | --- |
| `GET` | `/api/categories/` | Categoryの一覧取得 |
| `POST` | `/api/categories/` | Categoryの作成 |
| `GET` | `/api/categories/{id}/` | Categoryの詳細取得 |
| `PUT` | `/api/categories/{id}/` | Category全体の更新 |
| `PATCH` | `/api/categories/{id}/` | Categoryの部分更新 |
| `DELETE` | `/api/categories/{id}/` | Categoryの削除 |

一覧は結果が一定になるよう、`created_at`、`id`の順で返します。

### リクエスト項目

| 項目 | 必須 | 説明 |
| --- | --- | --- |
| `company` | 作成時は必須 | Categoryが所属するCompanyのUUID |
| `name` | 作成時は必須 | Category名。1文字以上255文字以下 |
| `parent_category` | 任意 | 親CategoryのUUID。`null`を指定可能 |

`id`、`created_at`、`updated_at`はサーバー側で設定する読み取り専用項目です。

### 作成例

```http
POST /api/categories/
Content-Type: application/json

{
  "company": "11111111-1111-1111-1111-111111111111",
  "name": "Backend",
  "parent_category": null
}
```

成功時は、作成されたCategoryを`201 Created`で返します。

```json
{
  "id": "22222222-2222-2222-2222-222222222222",
  "company": "11111111-1111-1111-1111-111111111111",
  "name": "Backend",
  "parent_category": null,
  "created_at": "2026-07-28T00:00:00Z",
  "updated_at": "2026-07-28T00:00:00Z"
}
```

## バリデーションとデータ整合性

以下の入力や状態を検証します。

- `company`と`name`の組み合わせが同一企業内で重複していないこと
- `name`が空ではなく、モデルの最大長255文字以内であること
- Companyおよび親CategoryのUUID形式と存在
- 親Categoryが同じCompanyに所属していること
- Category自身を親に指定していないこと
- 親子関係が循環参照にならないこと
- Company変更後も既存の親子関係が同一企業内に保たれること

通常のSerializerバリデーションに加え、検証後に発生し得る一意制約・外部キー制約の競合も捕捉し、`500 Internal Server Error`ではなく項目に対応した`400 Bad Request`を返します。

階層変更はトランザクション内で関係するCompanyとCategoryをロックし、保存直前の状態で再検証します。これにより、同時更新によって循環参照が作成されることを防ぎます。一方、親を持たない作成や名前だけの更新では企業単位のロックを使用せず、無関係な書き込みを必要以上に直列化しません。

更新対象が検証後に削除された場合は、リソースが存在しないことを示す`404 Not Found`を返します。

## 削除時の動作

既存モデルの制約に従います。

- Companyを削除した場合、所属するCategoryも削除されます（`CASCADE`）
- 親Categoryを削除した場合、子Categoryは残り、`parent_category`が`null`になります（`SET_NULL`）

## セットアップ

### 必要な環境

- Python 3.11
- PostgreSQL
- Pipenv

依存パッケージをインストールします。

```shell
pipenv install
```

PostgreSQLの接続情報は次の環境変数で指定できます。

| 環境変数 | デフォルト値 |
| --- | --- |
| `POSTGRES_DB` | `coding-test` |
| `POSTGRES_USER` | `root` |
| `POSTGRES_PASSWORD` | `password` |
| `DB_HOST_NAME` | `localhost` |
| `DB_PORT` | `5432` |

migrationを適用します。

```shell
pipenv run python manage.py migrate
```

開発サーバーを起動します。

```shell
pipenv run python manage.py runserver
```

## テスト

テストはDjangoのテストランナーからPostgreSQLのテストデータベースを使用して実行します。テスト用データベースを作成できる権限をPostgreSQLユーザーへ付与してください。

```shell
pipenv run python manage.py test
```

主なテスト対象は以下のとおりです。

- 一覧、詳細、作成、PUT、PATCH、削除の正常系
- 作成・更新レスポンスの全項目
- 存在しないIDと不正なUUID
- 必須項目不足、空の`name`、最大長超過
- 存在しないCompany・親Category
- `company`と`name`の重複
- 異なるCompanyの親Category、自己参照、循環参照
- 親子関係と矛盾するCompany変更
- 同時POST時の一意制約競合
- 検証後にCompany・親Category・更新対象が削除される競合
- 同時PATCHによる循環参照の防止

実装時点では、全31テストが成功しています。

## 主な変更ファイル

| ファイル | 役割 |
| --- | --- |
| `api/serializers/category.py` | 入出力定義、バリデーション、DB競合処理 |
| `api/views/category.py` | Category CRUD ViewSet |
| `api/urls.py` | RouterへのViewSet登録 |
| `api/models/__init__.py` | Company・Categoryモデルの登録 |
| `api/migrations/0001_initial.py` | 初期テーブル・制約・indexの作成 |
| `api/tests/test_views.py` | 正常系・異常系・競合系のAPIテスト |
