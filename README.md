# StoreRecord Category API

商品管理の基礎となるカテゴリ階層構造を管理するための API プロジェクトです。

## 1. 動作環境
*   **Docker** / **Docker Compose** がインストールされていること。

## 2. セットアップ手順

以下のコマンドをターミナルで順番に実行してください。

### ステップ 1: コンテナのビルドと起動
```bash
docker compose up --build -d
```

### ステップ 2: データベースの初期化（マイグレーション）
```bash
# マイグレーションファイルの作成
docker compose exec app python manage.py makemigrations api

# データベースへの反映
docker compose exec app python manage.py migrate
```

## 3. 動作確認の方法

### 方法 A: 自動テストによる検証（推奨）
実装されたバリデーション（循環参照防止、マルチテナント分離、削除制限等）を一括で検証します。
```bash
docker compose exec app python manage.py test api
```
**期待される結果:** `Ran 7 tests ... OK` と表示されること。

### 方法 B: ブラウザでの確認
Django REST Framework の Browsable API を利用して、視覚的に操作を確認できます。

1.  **デモ用データの作成:** 以下のコマンドで、確認用の企業データを作成します。
    ```bash
    docker compose exec app python manage.py shell -c "from api.models import Company; Company.objects.get_or_create(id='00000000-0000-0000-0000-000000000000', name='Demo Company')"
    ```
2.  **ブラウザでアクセス:** [http://localhost:8000/api/companies/00000000-0000-0000-0000-000000000000/categories/](http://localhost:8000/api/companies/00000000-0000-0000-0000-000000000000/categories/)
3.  **サンプルリクエスト (Raw dataに貼り付け可能):**
    *   **新規作成 (POST):** `{"name": "家電"}`
    *   **子の作成 (POST):** `{"name": "冷蔵庫", "parent_category_id": "親のUUID"}`
    *   **循環参照チェック (PATCH):** 親カテゴリの編集画面で、子のIDを `parent_category_id` に指定して送信するとエラーを返します。

## 4. 主な実装機能（独自拡張）
*   **循環参照の防止:** 親カテゴリ設定時に先祖ノードを遡って整合性を検証。
*   **マルチテナント分離:** URLパスの企業IDに基づくデータの論理分離。
*   **高度な削除バリデーション:** 子を持つカテゴリ削除時に、原因となる子IDリストを返却。
*   **ツリー構造変換:** GETリクエスト時にデータを木構造に変換して返却。

## 5. 実演・確認ケース (Browsable API)
ブラウザ上で、独自実装した高度な機能を以下の手順で確認できます。

### ケース1：再帰的なツリー構造の確認
1.  ルートカテゴリ（例: "家電"）を **POST** で作成し、レスポンスの `id` をコピーします。
2.  子カテゴリ（例: "冷蔵庫"）を **POST** で作成します。その際、`parent_category_id` に先ほどの UUID を指定します。
3.  一覧（GET）を取得すると、`children` 属性の中に子がネストされた、再帰的なツリー構造を確認できます。

### ケース2：高度な削除バリデーション
1.  子を持つカテゴリ（例: "家電"）の詳細画面で **DELETE** を実行します。
2.  `400 Bad Request` と共に、削除を妨げている子カテゴリの ID リスト（`blocking_child_ids`）が返却されることを確認できます。

### ケース3：循環参照（自己参照）の防止
1.  既存カテゴリの詳細画面で **PATCH** を実行します。
2.  `parent_category_id` に自分自身の `id` を指定して送信します。
3.  `A category cannot be its own parent.` というエラーメッセージが表示され、論理矛盾が阻止されることを確認できます。
