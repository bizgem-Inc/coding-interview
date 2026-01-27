# coding-interview

Django REST FrameworkとPostgreSQLを使用したAPIプロジェクト

## 前提条件

- WSL2
- Docker

## セットアップ方法

### ローカル開発環境のセットアップ（VSCode用）

VSCodeでインポートやコード補完を有効にするため、ローカルにPython環境を構築します。

#### 1. pyenvのインストール

```bash
# 必要なパッケージをインストール
sudo apt update
sudo apt install -y build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev curl \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

# pyenvをインストール
curl https://pyenv.run | bash

# .bashrcに設定を追加
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

# 設定を反映
source ~/.bashrc
```

#### 2. Python 3.11のインストール

```bash
# Python 3.11をインストール
pyenv install 3.11

# プロジェクトディレクトリでPython 3.11を使用
cd /home/mtsumura/projects/coding-interview
pyenv local 3.11
```

#### 3. 仮想環境の作成と有効化

```bash
# python3-venvパッケージをインストール（必要な場合）
sudo apt install -y python3-venv

# 仮想環境を作成
python -m venv venv

# 仮想環境を有効化
source venv/bin/activate
```

#### 4. 依存関係のインストール

```bash
# requirements.txtから依存関係をインストール
pip install --upgrade pip
pip install -r requirements.txt
```

#### 5. VSCodeでPythonインタープリタを選択

1. VSCodeでプロジェクトを開く
2. `Ctrl + Shift + P` でコマンドパレットを開く
3. `Python: Select Interpreter` を選択
4. `./venv/bin/python` を選択

### Dockerでのセットアップ

#### 1. 環境変数ファイルの作成

```bash
cp .env.sample .env
```

必要に応じて `.env` ファイルを編集してください。

### 3. Dockerコンテナの起動

```bash
docker compose up -d --build
```

※ 初回起動時は、イメージのビルドとデータベースのマイグレーションが自動的に実行される

### 4. アプリケーションへのアクセス

ブラウザで以下のURLにアクセスしてください：

```
http://localhost:8000
```

### 5. pgAdmin（データベース管理ツール）の設定

pgAdminは、PostgreSQLデータベースを視覚的に管理できるWebベースのツールです。

#### pgAdminへのアクセス

ブラウザで以下のURLにアクセスしてください：

```
http://localhost:5050
```

#### 初回ログイン

デフォルトの認証情報（`.env`ファイルで変更可能）：
- Email: `admin@example.com`
- Password: `admin`

#### PostgreSQLサーバーの登録（初回のみ）

1. pgAdminにログイン後、左側のサーバーツリーで「Servers」を右クリック
2. 「Register」→「Server...」を選択
3. 「General」タブ:
   - Name: `Coding Interview DB`（任意の名前）
4. 「Connection」タブ:
   - Host name/address: `db`
   - Port: `5432`
   - Maintenance database: `coding-test`（`.env`の`POSTGRES_DB`と同じ）
   - Username: `root`（`.env`の`POSTGRES_USER`と同じ）
   - Password: `password`（`.env`の`POSTGRES_PASSWORD`と同じ）
   - Save password: チェックを入れる（推奨）
5. 「Save」をクリック

**注意**: サーバー設定はpgAdminのボリュームに保存されるため、コンテナを再起動しても設定は保持されます。

## VSCodeでのリモートデバッグ

### 1. DEBUGモードを有効化

`.env`ファイルで以下を設定：
```bash
DEBUG=True
```

### 2. Dockerコンテナを起動

```bash
docker compose up -d
```

コンテナが debugpy の接続を待機します。

### 3. VS Codeでデバッガーをアタッチ

1. VS Codeで「実行とデバッグ」パネルを開く（Ctrl+Shift+D）
2. 「Python: Remote Attach (Docker)」を選択
3. F5 キーを押してデバッガーをアタッチ

### 4. デバッグ開始

- ブレークポイントを設定したいファイルで行番号の左側をクリック
- APIエンドポイントにアクセスするとブレークポイントで停止

### 通常モード（デバッグなし）

```bash
DEBUG=False docker compose up
```

## テストデータの投入

プロジェクトにはSeederコマンドが用意されており、SwaggerUIでAPIの動作確認を行うためのテストデータを簡単に投入できます。

### Seederの実行

```bash
docker compose exec app python manage.py seed
```

このコマンドを実行すると、以下のテストデータが自動的に作成されます：

- **企業データ**: 3社（株式会社テストカンパニーA、B、C）
- **カテゴリデータ**: 各企業に複数のカテゴリ（親カテゴリと子カテゴリを含む）

### 投入されるデータの例

#### 株式会社テストカンパニーA
- 電化製品（親）
  - テレビ（子）
  - 冷蔵庫（子）
- 家具（親）
  - ソファ（子）

#### 株式会社テストカンパニーB
- 食品（親）
  - 野菜（子）
  - 果物（子）

#### 株式会社テストカンパニーC
- 書籍（親）
- 文房具（親）

**注意**: Seederを実行すると、既存の企業とカテゴリデータは全て削除されます。

## SwaggerUIでのAPI動作確認

### SwaggerUIへのアクセス

```
http://localhost:8000/api/docs/
```

### Category APIエンドポイント一覧

以下のエンドポイントをSwaggerUI上で動作確認できます：

1. **GET /api/categories/** - カテゴリ一覧取得
2. **GET /api/categories/{id}/** - 特定カテゴリ取得（IDはSeederで作成されたUUID）
3. **POST /api/categories/** - カテゴリ作成
4. **PUT /api/categories/{id}/** - カテゴリ全体更新
5. **PATCH /api/categories/{id}/** - カテゴリ部分更新
6. **DELETE /api/categories/{id}/** - カテゴリ削除

### 動作確認手順（正常系）

#### 1. カテゴリ一覧取得
1. SwaggerUIで「GET /api/categories/」をクリック
2. 「Try it out」→「Execute」をクリック
3. Seederで作成したカテゴリ一覧が表示されることを確認

#### 2. 特定カテゴリ取得
1. 一覧取得で確認したカテゴリのIDをコピー
2. 「GET /api/categories/{id}/」をクリック
3. 「Try it out」→ id欄にUUIDを貼り付け→「Execute」
4. 該当カテゴリの詳細が表示されることを確認

#### 3. カテゴリ作成
1. 「POST /api/categories/」をクリック
2. 「Try it out」→ Request bodyに以下のようなJSONを入力：
```json
{
  "company": "Seederで作成された企業のUUID",
  "name": "新しいカテゴリ",
  "parent_category": null
}
```
3. 「Execute」→ 201 Createdが返されることを確認

#### 4. カテゴリ更新（PUT）
1. 「PUT /api/categories/{id}/」をクリック
2. 「Try it out」→ idとRequest bodyを入力
3. 「Execute」→ 200 OKが返されることを確認

#### 5. カテゴリ部分更新（PATCH）
1. 「PATCH /api/categories/{id}/」をクリック
2. 「Try it out」→ 更新したいフィールドのみ入力（例: `{"name": "更新後の名前"}`）
3. 「Execute」→ 200 OKが返されることを確認

#### 6. カテゴリ削除
1. 「DELETE /api/categories/{id}/」をクリック
2. 「Try it out」→ 削除対象のidを入力
3. 「Execute」→ 204 No Contentが返されることを確認

## よく使うコマンド

### コンテナの起動

```bash
docker compose up -d
```

### コンテナの停止

```bash
docker compose down
```

### コンテナの再起動

```bash
docker compose restart
```

### ログの確認

```bash
# 全てのコンテナのログ
docker compose logs -f

# 特定のコンテナのログ
docker compose logs -f app
docker compose logs -f db
```

### マイグレーションの実行

```bash
docker compose exec app python manage.py migrate
```

### マイグレーションファイルの作成

```bash
docker compose exec app python manage.py makemigrations
```

### 管理者ユーザーの作成

```bash
docker compose exec app python manage.py createsuperuser
```

### Djangoシェルの起動

```bash
docker compose exec app python manage.py shell
```

### テストの実行

```bash
docker compose exec app python manage.py test
```

### コンテナ内でコマンドを実行

```bash
docker compose exec app bash
```

## プロジェクト構成

```
.
├── api/                    # APIアプリケーション
│   ├── management/        # Django管理コマンド
│   │   └── commands/     # カスタムコマンド
│   │       └── seed.py   # テストデータ投入コマンド
│   ├── migrations/        # マイグレーションファイル（コマンドにより自動生成）
│   ├── models/            # データモデル
│   │   ├── category.py   # Categoryモデル
│   │   └── company.py    # Companyモデル
│   ├── serializers/       # シリアライザー・バリデーション
│   │   └── category.py   # Categoryシリアライザー
│   ├── views/             # ビュー・エンドポイント
│   │   └── category.py   # Categoryビューセット
│   └── tests/             # テスト
├── config/                # Django設定
│   ├── settings.py       # プロジェクト設定
│   └── urls.py           # URLルーティング
├── docker/                # Docker関連ファイル
│   └── app/
│       ├── Dockerfile    # Dockerイメージ定義
│       └── entrypoint.sh # コンテナ起動スクリプト
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
docker compose down -v
docker compose up -d --build
```

### コンテナを完全にクリーンアップ

```bash
docker compose down -v --rmi all
docker compose up -d --build
```
