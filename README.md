# coding-interview

## 実行方法

### 実行環境

- Docker Desktop が使える、もしくは`docker compose`に準ずる挙動ができる環境

### 実行コマンド

API サーバを起動する場合

```bash
# imageのビルド
docker compose build

# apiサーバ起動
# URI localhost:8000/api/categories
docker compose up api
```

テストのみ実行

```bash
# imageのビルドが終了している前提
# 以下コマンドにて、./htmlcov/index.html にカバレッジ結果を出力
./run_test.sh
```
