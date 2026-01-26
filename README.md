# coding-interview

Django REST FrameworkとPostgreSQLを使用したAPIプロジェクト

## 前提条件

- WSL2
- Docker
- Docker Compose

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
docker-compose up -d --build
```

※ 初回起動時は、イメージのビルドとデータベースのマイグレーションが自動的に実行される

### 4. アプリケーションへのアクセス

ブラウザで以下のURLにアクセスしてください：

```
http://localhost:8000
```

## VSCodeでのリモートデバッグ

### 1. DEBUGモードを有効化

`.env`ファイルで以下を設定：
```bash
DEBUG=True
```

### 2. Dockerコンテナを起動

```bash
docker-compose up -d
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
DEBUG=False docker-compose up
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
