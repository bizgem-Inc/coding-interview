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
ブラウザで `http://localhost:8000/api/` にアクセスすることで、Django REST Framework の Browsable API を利用して操作を確認できます。

## 4. 主な実装機能（独自拡張）
*   **循環参照の防止:** 親カテゴリ設定時に先祖ノードを遡って整合性を検証。
*   **マルチテナント分離:** URLパスの企業IDに基づくデータの論理分離。
*   **高度な削除バリデーション:** 子を持つカテゴリ削除時に、原因となる子IDリストを返却。
*   **ツリー構造変換:** GETリクエスト時にデータを木構造に変換して返却。
