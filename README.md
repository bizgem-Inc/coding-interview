# coding-interview

## 元ソースに対する変更内容
### model を一部変更しました
* Category - parent_category : blank=True を追加
  * 理由：最初の Category を作るため
### python パッケージの追加
* django-filte パッケージを追加
  * 理由：company.name, name, parent_category.name での検索を実装したため

## その他
### views/company.py の追加
管理画面から Company をできるようにするため、views/company.py を追加しています。
  
## API 機能一覧
|method|エンドポイント|名前|機能|
| ---- | ---- | ---- | ---- |
| GET  |/api/category/|一覧取得|全Category取得|
| GET  |/api/category/{id}|個別取得|id={id}のCategoryを取得|
| GET  |/api/category?name={name}|検索取得|name={name}のCategoryを取得|
| GET  |/api/category?company={name}|検索取得|company.name={name}のCategoryを取得|
| GET  |/api/category?parent_category={name}|検索取得|parent_category.name={name}のCategoryを取得|
| POST<sup>*</sup>|/api/category/|新規作成|Category新規作成|
| PUT<sup>*</sup>|/api/category/{id}/|一部更新|特定のCategoryの内容を更新|
|DELETE|/api/category/{id}/|個別削除|特定のCategoryを削除|

\* POST/PUT で parent_category を省略すると, parent_category が未設定(null)となります。