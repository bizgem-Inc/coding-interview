# coding-interview

Django REST FrameworkとPostgreSQLを使用したAPIプロジェクト

## 前提条件

- WSL2
- Docker
- Docker Compose

## セットアップ方法

### 2. 環境変数ファイルの作成

```bash
cp .env.sample .env
```

必要に応じて `.env` ファイルを編集してください。

### 3. Dockerコンテナの起動

```bash
docker-compose up -d --build
```

※ 初回起動時は、イメージのビルドとデータベースのマイグレーションが自動的に実行される

### 4. アプリケーションへのアクセス

ブラウザで以下のURLにアクセスしてください：

```
http://localhost:8000
```

## よく使うコマンド

### コンテナの起動

```bash
docker-compose up -d
```

### コンテナの停止

```bash
docker-compose down
```

### コンテナの再起動

```bash
docker-compose restart
```

### ログの確認

```bash
# 全てのコンテナのログ
docker-compose logs -f

# 特定のコンテナのログ
docker-compose logs -f app
docker-compose logs -f db
```

### マイグレーションの実行

```bash
docker-compose exec app python manage.py migrate
```

### マイグレーションファイルの作成

```bash
docker-compose exec app python manage.py makemigrations
```

### 管理者ユーザーの作成

```bash
docker-compose exec app python manage.py createsuperuser
```

### Djangoシェルの起動

```bash
docker-compose exec app python manage.py shell
```

### テストの実行

```bash
docker-compose exec app python manage.py test
```

### コンテナ内でコマンドを実行

```bash
docker-compose exec app bash
```

## プロジェクト構成

```
.
├── api/                    # APIアプリケーション
│   ├── models/            # データモデル
│   ├── serializers/       # シリアライザー・バリデーション
│   ├── views/             # ビュー・エンドポイント
│   └── tests/             # テスト
├── config/                # Django設定
├── docker/                # Docker関連ファイル
│   ├── Dockerfile         # Dockerイメージ定義
│   └── entrypoint.sh      # コンテナ起動スクリプト
├── docker-compose.yml     # Docker Compose設定
├── .env.sample           # 環境変数サンプル
├── requirements.txt      # Python依存関係
└── manage.py             # Django管理スクリプト
```

## トラブルシューティング

### ポートが既に使用されている場合

`.env` ファイルで `DB_PORT` を変更してください。

### データベースをリセットしたい場合

```bash
docker-compose down -v
docker-compose up -d --build
```

### コンテナを完全にクリーンアップ

```bash
docker-compose down -v --rmi all
docker-compose up -d --build
```
