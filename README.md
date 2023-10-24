# coding-interview

## 環境構築

### 依存必要ソフトウェア一覧

- MacOS
  - docker for mac
- WindowsOS
  - docker for windows
- LinuxOS
  - docker
  - docker compose

### dockerコンテナ起動コマンド
```
docker compose up -d
docker ps // コンテナが立ち上がっていることを確認
```

### サーバー起動


```
docker exec -it coding-interview-api bash
cd /app/src
pipenv shell
python manage.py runserver 0.0.0.0:8000 --settings config.settings_local
```


### テスト実行


```
docker exec -it coding-interview-api bash
cd /app/src
pipenv shell
python manage.py test --settings config.settings_local
```
