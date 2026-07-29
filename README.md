# coding-interview

このリポジトリは、コーディングテストのためのリポジトリです。

Django REST Frameworkを使用したAPIプロジェクトです。

企業（Company）に属するカテゴリ（Category）を管理し、カテゴリの一覧取得・詳細取得・作成・更新・削除を行えます。認証は必要ありません。

## 動作環境

- Python 3.11
- PostgreSQL
- Pipenv

## 環境構築

依存パッケージをインストールします。

```shell
pipenv install
```

データベース接続には以下の環境変数を使用します。未指定の場合はデフォルト値が使用されます。

| 環境変数 | デフォルト値 |
| --- | --- |
| `POSTGRES_DB` | `coding-test` |
| `POSTGRES_USER` | `root` |
| `POSTGRES_PASSWORD` | `password` |
| `DB_HOST_NAME` | `localhost` |
| `DB_PORT` | `5432` |

接続先のPostgreSQLにデータベースを用意した後、migrationを適用します。

```shell
pipenv run python manage.py migrate
```

## 起動方法

開発サーバーを起動します。

```shell
pipenv run python manage.py runserver
```

起動後、ブラウザで `http://127.0.0.1:8000/api/categories/` を開くと、DRFのBrowsable APIを使用できます。

Categoryの作成にはCompanyのUUIDが必要です。Companyを作成するAPIはないため、動作確認用のCompanyはDjango shellから作成します。

```shell
pipenv run python manage.py shell
```

```python
from api.models import Company

company = Company.objects.create(name="テスト企業")
print(company.id)
```

## API

| HTTPメソッド | エンドポイント | 機能 |
| --- | --- | --- |
| `GET` | `/api/categories/` | カテゴリの一覧取得 |
| `POST` | `/api/categories/` | カテゴリの作成 |
| `GET` | `/api/categories/{id}/` | カテゴリの詳細取得 |
| `PUT` | `/api/categories/{id}/` | カテゴリの更新 |
| `PATCH` | `/api/categories/{id}/` | カテゴリの部分更新 |
| `DELETE` | `/api/categories/{id}/` | カテゴリの削除 |

Categoryのリクエスト項目は以下のとおりです。

| 項目 | 必須 | 説明 |
| --- | --- | --- |
| `company` | 必須 | Categoryが属するCompanyのUUID |
| `name` | 必須 | カテゴリ名 |
| `parent_category` | 任意 | 親CategoryのUUID。親を持たない場合は省略または`null` |

## テスト

以下のコマンドですべてのテストを実行します。

```shell
pipenv run python manage.py test
```
