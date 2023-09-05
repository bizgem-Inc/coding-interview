# coding-interview

## プロジェクト構成

``` txt
~/coding-interview$ tree -L 2
.
├── README.md
├── docker
│   └── python
│
├── docker-compose.yml
│
│     # セットアップ用のスクリプト
├── setup.sh
│
│     # 提供して頂いた元のファイル
├── src
│   ├── models
│   ├── serializers
│   ├── urls.py
│   └── views
│
│     # コーディングテスト用のDjangoプロジェクト
└── test_app
    ├── Category
    ├── Company
    ├── Pipfile
    ├── Pipfile.lock
    ├── config
    └── manage.py
```

## 環境構築

本環境はDocker、及びDockerComposeがホストマシンにインストールされている前提です。  
Docker本体のインストールに関しては割愛します。

### セットアップ

``` sh
# セットアップ
$ cd [project]
$ chmod +x ./setup.sh
$ ./setup.sh

# 機密情報や環境の設定を編集
$ vi .env
```

### 開発環境の起動

``` sh
# Docker環境のビルド
$ docker compose build

# Docker環境の立ち上げ
$ docker compose up -d

# コンテナ内へのアクセス
$ docker compose exec app bash

# DB Migrate
$ python manage.py migrate

# コンテナから出る(コンテナ内にいる場合)
$ exit

# Docker環境の停止
$ docker compose down
```

### パッケージのインストール

本プロジェクトでは、pipenvを採用しているため、Docker内でのパッケージインストールの手間は考慮しないものとする  
本来は、Dockerを使用している時点で環境として独立しているため、pipenvは採用しない

``` sh
# コンテナ内へのアクセス
$ docker compose exec app bash

# プロジェクト専用のpipに切り替え
(in container)$ pipenv shell

# パッケージのインストール
(in container)$ pipenv install [package name]

# コンテナから出て、コンテナを落とす
(in container)$ exit
$ docker compose down

# 再度、コンテナイメージをビルド
$ docker compose build
```

## APIの確認

### サーバーの立ち上げ
``` sh
# コンテナの立ち上げ
# この時点で、自動的にサーバーが立ち上がる
$ docker compose up -d
```

### API

前提： ポートは.env内で設定した任意のポート、又は8000です。

[http://localhost:8000/api/categories/](http://localhost:8000/api/categories/)へアクセスするとカテゴリ一覧が表示されます。

以下のいづれかのツールを使って操作してください

- Django REST framework
- Postman
- Curl
