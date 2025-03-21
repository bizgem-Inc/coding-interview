# 環境構築

アプリケーション用の仮想環境を作成する
```bash
# pipenv がない場合
pip install pipenv

pipenv install
pipenv shell
```

DB を起動する
```bash
docker compose up -d
```

migrate する
```bash
python manage.py migrate
```

# テスト

```bash
python manage.py test
```
