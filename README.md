# coding-interview

### 起動方法
DBはpostgresをdockerで起動する前提です。
```sh
% docker-compose up
```

pipenvのコマンドを使い仮想環境の準備、ライブラリのインストールを行います
```sh
% pipenv shell
```
```sh
% pipenv sync
```

migrationの実行
```sh
python3 manage.py migrate
```

サーバ起動
```sh
% python manage.py runserver
```


### APIコール例
事前にcomapniesのレコードがinsertされている前提です。
insert例
```sql
insert into companies (id, name, created_at, updated_at) values(gen_random_uuid(), 'test', now(), now());
```

- カテゴリ作成
```sh
% curl -X POST -H "Content-Type: application/json" -d '{"name" : "test_1" , "company_id" : "769ffc60-49fc-406e-816b-d6893c0b6aa0"}' http://127.0.0.1:8000/api/categories/
{"id":"0c39f577-ca75-4a9c-82e2-db0b1936a56e","parent_category":null,"company":{"id":"769ffc60-49fc-406e-816b-d6893c0b6aa0","name":"test","created_at":"2023-12-10T12:02:28.878737Z","updated_at":"2023-12-10T12:02:28.878754Z"},"name":"test_1","created_at":"2023-12-15T14:19:25.292559Z","updated_at":"2023-12-15T14:19:25.292578Z"}
```

- カテゴリの更新
```sh
% curl -X PUT -H "Content-Type: application/json" -d '{"name" : "test_1_1" , "company_id" : "769ffc60-49fc-406e-816b-d6893c0b6aa0"}' http://127.0.0.1:8000/api/categories/0c39f577-ca75-4a9c-82e2-db0b1936a56e/
{"id":"0c39f577-ca75-4a9c-82e2-db0b1936a56e","parent_category":null,"company":{"id":"769ffc60-49fc-406e-816b-d6893c0b6aa0","name":"test","created_at":"2023-12-10T12:02:28.878737Z","updated_at":"2023-12-10T12:02:28.878754Z"},"name":"test_1_1","created_at":"2023-12-15T14:19:25.292559Z","updated_at":"2023-12-15T14:29:18.283564Z"}%
```

- カテゴリの一覧表示
```sh
% curl -X GET http://127.0.0.1:8000/api/categories/
[{"id":"0c39f577-ca75-4a9c-82e2-db0b1936a56e","parent_category":null,"company":{"id":"769ffc60-49fc-406e-816b-d6893c0b6aa0","name":"test","created_at":"2023-12-10T12:02:28.878737Z","updated_at":"2023-12-10T12:02:28.878754Z"},"name":"test_1_1","created_at":"2023-12-15T14:19:25.292559Z","updated_at":"2023-12-15T14:29:18.283564Z"}]%
```

- カテゴリを取得
```sh
% curl -X GET http://127.0.0.1:8000/api/categories/0c39f577-ca75-4a9c-82e2-db0b1936a56e/
{"id":"0c39f577-ca75-4a9c-82e2-db0b1936a56e","parent_category":null,"company":{"id":"769ffc60-49fc-406e-816b-d6893c0b6aa0","name":"test","created_at":"2023-12-10T12:02:28.878737Z","updated_at":"2023-12-10T12:02:28.878754Z"},"name":"test_1_1","created_at":"2023-12-15T14:19:25.292559Z","updated_at":"2023-12-15T14:29:18.283564Z"}% 
```

- カテゴリ削除
```sh
% curl -X DELETE http://127.0.0.1:8000/api/categories/0c39f577-ca75-4a9c-82e2-db0b1936a56e/
```
