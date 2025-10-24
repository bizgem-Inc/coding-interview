# coding-interview

Django REST Framework を使用したカテゴリ管理APIのバックエンドプロジェクト

## 目次

- [技術スタック](#技術スタック)
- [セットアップ](#セットアップ)
- [データモデル](#データモデル)
- [API仕様](#api仕様)
- [テスト](#テスト)
- [プロジェクト構造](#プロジェクト構造)

## 技術スタック

- **Python**: 3.11
- **Django**: 4.2+
- **Django REST Framework**: 最新版
- **PostgreSQL**: データベース
- **psycopg2**: PostgreSQLアダプター

## セットアップ

### 前提条件

以下がインストールされている必要があります：

- **Python 3.11**
- **pipenv** (Python仮想環境管理ツール)
- **PostgreSQL** (データベース)

### 1. リポジトリのクローン

```bash
git clone https://github.com/bizgem-Inc/coding-interview.git
cd coding-interview
```

### 2. Python 3.11の確認

```bash
python3 --version
# Python 3.11.x と表示されることを確認
```

Python 3.11がインストールされていない場合は、[公式サイト](https://www.python.org/downloads/)からインストールしてください。

### 3. pipenvのインストール

pipenvがインストールされていない場合：

```bash
pip3 install pipenv
```

### 4. PostgreSQLのセットアップ

#### PostgreSQLのインストール

**macOS（Homebrew使用）:**
```bash
brew install postgresql@14
brew services start postgresql@14
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows:**
[PostgreSQL公式サイト](https://www.postgresql.org/download/windows/)からインストーラーをダウンロードしてインストール

#### データベースとユーザーの作成

```bash
# PostgreSQLに接続
psql postgres

# データベースとユーザーを作成（PostgreSQLプロンプト内で実行）
CREATE USER root WITH PASSWORD 'password' CREATEDB;
CREATE DATABASE "coding-test" OWNER root;
GRANT ALL PRIVILEGES ON DATABASE "coding-test" TO root;

# スキーマ権限の付与
\c coding-test
GRANT ALL ON SCHEMA public TO root;

# 終了
\q
```

### 5. 仮想環境の構築と依存関係のインストール

```bash
# 仮想環境を作成し、依存関係をインストール
pipenv install

# 仮想環境をアクティベート（必要に応じて）
pipenv shell
```

### 6. 環境変数の設定（オプション）

デフォルト値が設定されていますが、必要に応じて環境変数で上書きできます：

```bash
export POSTGRES_DB=coding-test
export POSTGRES_USER=root
export POSTGRES_PASSWORD=password
export DB_HOST_NAME=localhost
export DB_PORT=5432
```

または `.env` ファイルを作成：

```env
POSTGRES_DB=coding-test
POSTGRES_USER=root
POSTGRES_PASSWORD=password
DB_HOST_NAME=localhost
DB_PORT=5432
```

### 7. データベースのマイグレーション

```bash
# マイグレーションディレクトリの作成
mkdir -p api/migrations
touch api/migrations/__init__.py

# マイグレーションファイルの生成
pipenv run python manage.py makemigrations api

# データベースへの適用
pipenv run python manage.py migrate
```

### 8. 開発サーバーの起動

```bash
pipenv run python manage.py runserver
```

サーバーは `http://localhost:8000` で起動します。

## データモデル

### Company（企業）

企業情報を管理するモデル

| フィールド | 型 | 説明 |
|-----------|-----|------|
| id | UUIDField | 企業ID（主キー、自動生成） |
| name | CharField(255) | 企業名 |
| created_at | DateTimeField | 作成日時（自動設定） |
| updated_at | DateTimeField | 更新日時（自動更新） |

### Category（カテゴリ）

カテゴリ情報を管理するモデル。階層構造をサポート。

| フィールド | 型 | 説明 |
|-----------|-----|------|
| id | UUIDField | カテゴリID（主キー、自動生成） |
| company | ForeignKey(Company) | 企業ID（外部キー、CASCADE削除） |
| name | CharField(255) | カテゴリ名 |
| parent_category | ForeignKey(self) | 親カテゴリID（NULL許可、SET_NULL削除） |
| created_at | DateTimeField | 作成日時（自動設定） |
| updated_at | DateTimeField | 更新日時（自動更新） |

#### 制約

- **一意制約**: `(company, name)` の組み合わせは一意である必要があります
- **インデックス**: `(company, name)` フィールドにインデックスが設定されています

#### 階層構造

`parent_category` フィールドを使用して、カテゴリの親子関係を表現できます：

```
カテゴリA (parent_category = null)
  └─ カテゴリB (parent_category = カテゴリA)
      └─ カテゴリC (parent_category = カテゴリB)
```

## API使用ガイド

### サーバーの起動

APIを使用する前に、開発サーバーを起動してください：

```bash
pipenv run python manage.py runserver
```

サーバーは `http://localhost:8000` で起動します。

### 企業（Company）データの作成

カテゴリを作成する前に、企業データが必要です。Django shellで作成できます：

```bash
pipenv run python manage.py shell
```

shellで以下を実行：

```python
from api.models.company import Company

# 企業を作成
company = Company.objects.create(name="Your Company Name")
print(f"Company ID: {company.id}")
```

作成された `Company ID` をメモしてください。

### APIテストツール

以下のいずれかの方法でAPIをテストできます：

#### 1. ブラウザ（最も簡単）

サーバー起動後、ブラウザで以下のURLを開く：

```
http://localhost:8000/api/categories/
```

Django REST FrameworkのWeb UIが表示され、GUIでAPIを操作できます。

#### 2. curlコマンド（ターミナル）

```bash
# カテゴリ一覧を取得
curl http://localhost:8000/api/categories/

# 見やすく整形
curl http://localhost:8000/api/categories/ | python -m json.tool
```

#### 3. その他のツール

- **Postman** - GUI APIクライアント
- **Insomnia** - GUI APIクライアント
- **HTTPie** - `pip install httpie` 後、`http GET localhost:8000/api/categories/`

---

## API仕様

ベースURL: `http://localhost:8000/api/`

すべてのエンドポイントは認証不要です（開発・テスト用）。

### エンドポイント一覧

| メソッド | エンドポイント | 説明 |
|---------|--------------|------|
| GET | `/api/categories/` | カテゴリ一覧取得 |
| POST | `/api/categories/` | カテゴリ作成 |
| GET | `/api/categories/{id}/` | カテゴリ詳細取得 |
| PUT | `/api/categories/{id}/` | カテゴリ更新（全フィールド） |
| PATCH | `/api/categories/{id}/` | カテゴリ部分更新 |
| DELETE | `/api/categories/{id}/` | カテゴリ削除 |

---

### GET `/api/categories/`

カテゴリ一覧を取得します。

#### 使い方

**curlコマンド:**

```bash
curl -X GET http://localhost:8000/api/categories/
```

**ブラウザ:**

```
http://localhost:8000/api/categories/
```

ブラウザで開くと、Django REST FrameworkのWeb UIが表示されます。

#### レスポンス例

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "company": "660e8400-e29b-41d4-a716-446655440000",
    "name": "Electronics",
    "parent_category": null,
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-01-15T10:30:00Z"
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "company": "660e8400-e29b-41d4-a716-446655440000",
    "name": "Smartphones",
    "parent_category": "550e8400-e29b-41d4-a716-446655440000",
    "created_at": "2025-01-15T10:31:00Z",
    "updated_at": "2025-01-15T10:31:00Z"
  }
]
```

#### ステータスコード

- `200 OK`: 成功

---

### POST `/api/categories/`

新しいカテゴリを作成します。

#### 使い方

**curlコマンド（親カテゴリを作成）:**

```bash
curl -X POST http://localhost:8000/api/categories/ \
  -H "Content-Type: application/json" \
  -d '{
    "company": "YOUR_COMPANY_ID",
    "name": "Electronics"
  }'
```

**curlコマンド（子カテゴリを作成）:**

```bash
curl -X POST http://localhost:8000/api/categories/ \
  -H "Content-Type: application/json" \
  -d '{
    "company": "YOUR_COMPANY_ID",
    "name": "Smartphones",
    "parent_category": "PARENT_CATEGORY_ID"
  }'
```

`YOUR_COMPANY_ID` と `PARENT_CATEGORY_ID` は実際のUUIDに置き換えてください。

**ブラウザ:**

1. `http://localhost:8000/api/categories/` を開く
2. ページ下部の「POST」フォームに入力
3. 「POST」ボタンをクリック

#### リクエストボディ

```json
{
  "company": "660e8400-e29b-41d4-a716-446655440000",
  "name": "Books",
  "parent_category": null
}
```

#### フィールド説明

| フィールド | 必須 | 型 | 説明 |
|-----------|-----|-----|------|
| company | ✓ | UUID | 企業ID |
| name | ✓ | string | カテゴリ名（最大255文字） |
| parent_category | - | UUID or null | 親カテゴリID（任意） |

#### レスポンス例

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "company": "660e8400-e29b-41d4-a716-446655440000",
  "name": "Books",
  "parent_category": null,
  "created_at": "2025-01-15T10:32:00Z",
  "updated_at": "2025-01-15T10:32:00Z"
}
```

#### ステータスコード

- `201 Created`: 作成成功
- `400 Bad Request`: バリデーションエラー
  - 同じ企業内で同じ名前のカテゴリが既に存在する場合
  - 必須フィールドが不足している場合

---

### GET `/api/categories/{id}/`

指定されたIDのカテゴリ詳細を取得します。

#### 使い方

**curlコマンド:**

```bash
curl -X GET http://localhost:8000/api/categories/YOUR_CATEGORY_ID/
```

`YOUR_CATEGORY_ID` は実際のカテゴリIDに置き換えてください。

**ブラウザ:**

```
http://localhost:8000/api/categories/YOUR_CATEGORY_ID/
```

#### パスパラメータ

- `id` (UUID): カテゴリID

#### レスポンス例

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "company": "660e8400-e29b-41d4-a716-446655440000",
  "name": "Electronics",
  "parent_category": null,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

#### ステータスコード

- `200 OK`: 成功
- `404 Not Found`: 指定されたIDのカテゴリが存在しない

---

### PUT `/api/categories/{id}/`

指定されたIDのカテゴリを更新します（全フィールド必須）。

#### 使い方

**curlコマンド:**

```bash
curl -X PUT http://localhost:8000/api/categories/YOUR_CATEGORY_ID/ \
  -H "Content-Type: application/json" \
  -d '{
    "company": "YOUR_COMPANY_ID",
    "name": "Updated Category Name"
  }'
```

**ブラウザ:**

1. `http://localhost:8000/api/categories/YOUR_CATEGORY_ID/` を開く
2. ページ下部の「PUT」フォームに全フィールドを入力
3. 「PUT」ボタンをクリック

#### パスパラメータ

- `id` (UUID): カテゴリID

#### リクエストボディ

```json
{
  "company": "660e8400-e29b-41d4-a716-446655440000",
  "name": "Consumer Electronics",
  "parent_category": null
}
```

#### レスポンス例

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "company": "660e8400-e29b-41d4-a716-446655440000",
  "name": "Consumer Electronics",
  "parent_category": null,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:35:00Z"
}
```

#### ステータスコード

- `200 OK`: 更新成功
- `400 Bad Request`: バリデーションエラー
- `404 Not Found`: 指定されたIDのカテゴリが存在しない

---

### PATCH `/api/categories/{id}/`

指定されたIDのカテゴリを部分更新します（変更したいフィールドのみ送信）。

#### 使い方

**curlコマンド:**

```bash
curl -X PATCH http://localhost:8000/api/categories/YOUR_CATEGORY_ID/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Category Name"
  }'
```

**ブラウザ:**

1. `http://localhost:8000/api/categories/YOUR_CATEGORY_ID/` を開く
2. ページ下部の「PATCH」フォームに変更したいフィールドのみ入力
3. 「PATCH」ボタンをクリック

#### パスパラメータ

- `id` (UUID): カテゴリID

#### リクエストボディ例

```json
{
  "name": "Updated Category Name"
}
```

#### レスポンス例

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "company": "660e8400-e29b-41d4-a716-446655440000",
  "name": "Updated Category Name",
  "parent_category": null,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:36:00Z"
}
```

#### ステータスコード

- `200 OK`: 更新成功
- `400 Bad Request`: バリデーションエラー
- `404 Not Found`: 指定されたIDのカテゴリが存在しない

---

### DELETE `/api/categories/{id}/`

指定されたIDのカテゴリを削除します。

#### 使い方

**curlコマンド:**

```bash
curl -X DELETE http://localhost:8000/api/categories/YOUR_CATEGORY_ID/
```

**ブラウザ:**

1. `http://localhost:8000/api/categories/YOUR_CATEGORY_ID/` を開く
2. ページ下部の「DELETE」ボタンをクリック
3. 確認ダイアログで「Yes」を選択

#### パスパラメータ

- `id` (UUID): カテゴリID

#### レスポンス

レスポンスボディなし

#### ステータスコード

- `204 No Content`: 削除成功
- `404 Not Found`: 指定されたIDのカテゴリが存在しない

#### 注意事項

親カテゴリが削除された場合、子カテゴリの `parent_category` は `null` に設定されます（`SET_NULL`）。

---

## エラーレスポンス

### バリデーションエラー（400 Bad Request）

```json
{
  "name": [
    "This field is required."
  ]
}
```

または

```json
{
  "non_field_errors": [
    "The fields company, name must make a unique set."
  ]
}
```

### Not Found（404 Not Found）

```json
{
  "detail": "Not found."
}
```

---

## テスト

### テスト実行

```bash
pipenv run python manage.py test api.tests.test_views
```

### テストカバレッジ

`api/tests/test_views.py` には以下のテストが実装されています：

- **test_list**: カテゴリ一覧取得のテスト
- **test_retrieve**: 単一カテゴリ詳細取得のテスト
- **test_create**: カテゴリ作成のテスト
- **test_update**: カテゴリ更新（PUT）のテスト
- **test_destroy**: カテゴリ削除のテスト

各テストでは以下を検証しています：

- 正しいHTTPステータスコードが返されること
- レスポンスデータが期待通りであること
- データベースの状態が正しく変更されること

---

## プロジェクト構造

```
coding-interview/
├── api/                      # メインアプリケーション
│   ├── models/               # データモデル
│   │   ├── __init__.py
│   │   ├── category.py       # Categoryモデル
│   │   └── company.py        # Companyモデル
│   ├── serializers/          # シリアライザ
│   │   ├── __init__.py
│   │   └── category.py       # CategorySerializer
│   ├── views/                # ビュー
│   │   ├── __init__.py
│   │   └── category.py       # CategoryViewSet
│   ├── tests/                # テスト
│   │   ├── __init__.py
│   │   └── test_views.py     # CategoryViewTests
│   ├── urls.py               # URLルーティング
│   └── apps.py
├── config/                   # プロジェクト設定
│   ├── settings.py           # Django設定
│   ├── urls.py               # ルートURLconf
│   └── wsgi.py
├── manage.py                 # Django管理スクリプト
├── Pipfile                   # 依存関係定義
├── Pipfile.lock              # 依存関係ロックファイル
└── README.md                 # このファイル
```

---

## 開発ガイドライン

### コーディング規約

- PEP 8に準拠したPythonコード
- インポートは標準ライブラリ → サードパーティ → ローカルの順
- クラスや関数にはdocstringを記述

### コミットメッセージ

Conventional Commits形式を使用：

```
feat: 新機能
fix: バグ修正
docs: ドキュメント変更
test: テスト追加・修正
refactor: リファクタリング
chore: その他の変更
```


