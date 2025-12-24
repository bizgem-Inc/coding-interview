# coding-interview

## テスト実行ガイド

### 環境構築

#### 1. 仮想環境の作成と有効化

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 2. 依存パッケージのインストール

```bash
pip install django djangorestframework psycopg2-binary
```

---

### 自動テスト（単体テスト）

SQLite（インメモリ）を使用してテスト実行：

```bash
source venv/bin/activate
python -c "
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
import django
from django.conf import settings
settings.DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
django.setup()
from django.test.utils import get_runner
TestRunner = get_runner(settings)
test_runner = TestRunner()
failures = test_runner.run_tests(['api.tests.test_views'])
exit(failures)
"
```

#### テストケース一覧

| テストメソッド  | 説明                                         |
| --------------- | -------------------------------------------- |
| `test_list`     | カテゴリ一覧取得 (GET /api/categories/)      |
| `test_retrieve` | カテゴリ詳細取得 (GET /api/categories/{id}/) |
| `test_create`   | カテゴリ作成 (POST /api/categories/)         |
| `test_update`   | カテゴリ更新 (PUT /api/categories/{id}/)     |
| `test_destroy`  | カテゴリ削除 (DELETE /api/categories/{id}/)  |

---

### 手動テスト（curl）

#### 1. SQLite 用の設定ファイルを作成

```bash
cat << 'EOF' > config/settings_sqlite.py
from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
EOF
```

#### 2. マイグレーション作成・実行

```bash
source venv/bin/activate
python manage.py makemigrations api --settings=config.settings_sqlite
python manage.py migrate --settings=config.settings_sqlite
```

#### 3. 開発サーバー起動

```bash
python manage.py runserver --settings=config.settings_sqlite
```

#### 4. 別ターミナルで API テスト

##### 4.1 テスト用の Company を作成

```bash
source venv/bin/activate
python -c "
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings_sqlite'
import django
django.setup()
from api.models import Company
company = Company.objects.create(name='テスト企業')
print(f'Company ID: {company.id}')
"
```

出力された Company ID をメモしてください（例: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`）

##### 4.2 カテゴリ作成 (POST)

```bash
# {COMPANY_ID} を上記で取得したIDに置き換えてください
curl -X POST http://localhost:8000/api/categories/ \
  -H "Content-Type: application/json" \
  -d '{"company": "{COMPANY_ID}", "name": "カテゴリA"}'
```

**期待するレスポンス (201 Created):**

```json
{
  "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "company": "{COMPANY_ID}",
  "name": "カテゴリA",
  "parent_category": null,
  "created_at": "2025-12-24T...",
  "updated_at": "2025-12-24T..."
}
```

##### 4.3 カテゴリ一覧取得 (GET)

```bash
curl -X GET http://localhost:8000/api/categories/
```

**期待するレスポンス (200 OK):**

```json
[
  {
    "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "company": "{COMPANY_ID}",
    "name": "カテゴリA",
    "parent_category": null,
    "created_at": "2025-12-24T...",
    "updated_at": "2025-12-24T..."
  }
]
```

##### 4.4 カテゴリ詳細取得 (GET)

```bash
# {CATEGORY_ID} を作成時に取得したIDに置き換えてください
curl -X GET http://localhost:8000/api/categories/{CATEGORY_ID}/
```

**期待するレスポンス (200 OK):**

```json
{
  "id": "{CATEGORY_ID}",
  "company": "{COMPANY_ID}",
  "name": "カテゴリA",
  "parent_category": null,
  "created_at": "2025-12-24T...",
  "updated_at": "2025-12-24T..."
}
```

##### 4.5 カテゴリ更新 (PUT)

```bash
curl -X PUT http://localhost:8000/api/categories/{CATEGORY_ID}/ \
  -H "Content-Type: application/json" \
  -d '{"company": "{COMPANY_ID}", "name": "カテゴリA（更新）"}'
```

**期待するレスポンス (200 OK):**

```json
{
  "id": "{CATEGORY_ID}",
  "company": "{COMPANY_ID}",
  "name": "カテゴリA（更新）",
  "parent_category": null,
  "created_at": "2025-12-24T...",
  "updated_at": "2025-12-24T..."
}
```

##### 4.6 カテゴリ部分更新 (PATCH)

```bash
curl -X PATCH http://localhost:8000/api/categories/{CATEGORY_ID}/ \
  -H "Content-Type: application/json" \
  -d '{"name": "カテゴリB"}'
```

**期待するレスポンス (200 OK):**

```json
{
  "id": "{CATEGORY_ID}",
  "company": "{COMPANY_ID}",
  "name": "カテゴリB",
  "parent_category": null,
  "created_at": "2025-12-24T...",
  "updated_at": "2025-12-24T..."
}
```

##### 4.7 カテゴリ削除 (DELETE)

```bash
curl -X DELETE http://localhost:8000/api/categories/{CATEGORY_ID}/
```

**期待するレスポンス (204 No Content):**

- レスポンスボディなし

##### 4.8 削除確認

```bash
curl -X GET http://localhost:8000/api/categories/
```

**期待するレスポンス (200 OK):**

```json
[]
```

---

### クリーンアップ

テスト終了後、SQLite データベースを削除：

```bash
rm db.sqlite3
rm config/settings_sqlite.py
```
