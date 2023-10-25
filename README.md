# coding-interview

## 元ソースに対する変更内容
### model を一部変更しました
* Category - parent_category : blank=True を追加
  * 理由：最初の Category を作れないので
* django-filte パッケージを追加
  * 理由：company.name, name, parent_category.name で検索できるようにするため
　    

テスト時 WARNINGS が出力されます。これは開発環境に使った SQLite が db_comment に非対応なために出力されたものです。テスト自体には影響は有りません。


## API 機能一覧
|method|エンドポイント|名前|機能|
| ---- | ---- | ---- | ---- |
| GET  |/api/category/|一覧取得|全Category取得|
| GET  |/api/category/{id}|個別取得|id={id}のCategoryを取得|
| GET  |/api/category?name={name}|検索取得|name={name}のCategoryを取得|
| GET  |/api/category?company={name}|検索取得|company.name={name}のCategoryを取得|
| GET  |/api/category?parent_category={name}|検索取得|parent_category.name={name}のCategoryを取得|
| POST |/api/category/|新規作成|Category新規作成|
| PUT  |/api/category/{id}/|一部更新|特定のCategoryの内容を更新|
|DELETE|/api/category/{id}/|個別削除|特定のCategoryを削除|

