<<<<<<< HEAD
# coding-interview
=======
# coding-interview

## 元ソースに対する変更内容
### model を一部変更
* Category - parent_category : blank=True を追加
  * 理由：最初の Category を作るため
### python パッケージの追加
* django-filte パッケージを追加
  * 理由：company.name, name, parent_category.name での検索を実装したため

## その他
### views/company.py の追加
管理画面から Company を編集できるようにするため、views/company.py を追加
### 動作環境
settings.py の 'DATABASES' は変更していません。django-filte を追加 install すれば、元ソースの動いていた環境で動作確認出来るはずです。
  
## API 機能一覧
|method|エンドポイント|名前|機能|
| ---- | ---- | ---- | ---- |
| GET  |/api/category/|一覧取得|全Category取得|
| GET  |/api/category/{id}|個別取得|id={id}のCategoryを取得|
| GET  |/api/category?name={name}|検索取得|name={name}のCategoryを取得|
| GET  |/api/category?company={name}|検索取得|company.name={name}のCategoryを取得|
| GET  |/api/category?parent_category={name}|検索取得|parent_category.name={name}のCategoryを取得|
| POST<sup>*</sup>|/api/category/|新規作成|Category新規作成|
| PUT<sup>*</sup>|/api/category/{id}/|更新|{id}で指定されるCategoryの内容を更新|
|DELETE|/api/category/{id}/|個別削除|{id}で指定されたCategoryを削除|

\* POST/PUT で parent_category を省略すると, parent_category が未設定(null)となります。ブラウザから利用する場合は、'HTML form' ではなく Raw data' を使って API を呼び出してください。
>>>>>>> upstream/master
