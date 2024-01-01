coding-interview
==========

以下のレポジトリ内でCategoryモデルの読み取り・作成・更新・削除が出来るAPI (認証の考慮は不要) を実装し、Pull Requestの作成をお願いいたします。

https://github.com/bizgem-Inc/coding-interview

上記レポジトリ内で以下の実装を行いPull Requestのご作成をお願いいたします。

- Categoryモデルの読み取り・作成・更新・削除が出来るAPI
  ※ views/category.py, serializers/category.py に実装するイメージ
- APIのテストの実装 (出来れば)
  ※ test_views.pyに実装するイメージ


### 実行方法

本ソースを `git clone` のうえ、`make dev`でコンテナーを起動します。

### テスト実行方法

コンテナーを起動のうえ、`make test` でユニットテストが実行されます。