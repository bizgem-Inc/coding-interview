# coding-interview

model を一部変更しました
・Category - parent_category : blank=True を追加
    理由：最初の Category を作れないので

テスト時 WARNINGS が出力されます。これは開発環境に使った SQLite が db_comment に非対応なために出力されたものです。テスト自体には影響は有りません。


|method|エンドポイント|名前|機能|
| ---- | ---- | ---- | ---- |
| GET  |/api/category/|一覧取得|全Category取得|
| POST |/api/category/|新規作成|Category新規作成|
| GET  |/api/category/{id}|個別取得|特定のCategoryを取得|
| PUT  |/api/category/{id}|一部更新|特定のCategoryの内容を更新|
|DELETE|/api/category/{id}|個別削除|特定のCategoryを削除|

