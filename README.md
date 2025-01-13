# coding-interview
Apple Silicon の Mac で作成しています。

# 構成
元々あった api がその他のライブラリと重複していてうまく動作しなかったので、item_api という app に変更しています。

# 事前準備
Poetry を利用しているので [Poetry をインストール](https://formulae.brew.sh/formula/poetry)してください。

# Python のバージョン
3.11.0 です。[pyenv](https://github.com/pyenv/pyenv) をインストールしてセットしてください。

```commandline
brew install pyenv
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
pyenv install 3.11.0
pyenv local 3.11.0
```

# venv セット & activate
```commandline
python -m venv ./.venv
source ./.venv/bin/activate
```

# Poetry の実行
```commandline
poetry install --no-root
```

# マイグレーションファイルの実行
既存のモデルから作成したマイグレーションファイルからマイグレーションを実行します。
プロファイルはローカルを指定します。

```commandline
python manage.py migrate
```

# アプリケーションの実行
runserver で実行します。

````commandline
python manage.py runserver  
````

# テストの実行

````commandline
python manage.py test --settings=config.settings.test 
````

# API 
Company と Category があります。

## companies
企業の CRUD です。

```commandline
/api/companies
```

入れ替えないので、PUT はないです。PATCH で名前を更新します。

## categories
カテゴリの CRUD です。末尾スラッシュは Trail されているので指定しません。

| method | 例                                                         | 説明                                                                                |
|--------|-----------------------------------------------------------|-----------------------------------------------------------------------------------| 
| GET    | /api/categories/\<uuid>                                   | 指定されたカテゴリIDでカテゴリを取得します。                                                           
| GET    | /api/categories?company=\<uuid>&name=\<name>&page_size=10 | 指定されたクエリに基づいてカテゴリ一覧を取得します。name は前後方一致、page_size で取得件数を指定できます。                     |
| POST   | /api/categories                                           | company (必須), name (必須)、 parent_category(任意) でカテゴリリソースを作成します。企業ごとにカテゴリ名はユニークになります |
| PATCH  | /api/categories\<uuid>                                    | 指定されたリソースの company, name, parent_category を変更します。NULL が指定された場合変更しません。(親カテゴリ含む)    |
| PUT    | /api/categories\<uuid>                                    | 指定されたリソースを置き換えます。置き換えるので NULL で指定された場合置き換えを実行します。                                 |
| DELETE | /api/categories\<uuid>                                    | 指定されたリソースを削除します。親カテゴリに設定されたリソースである場合、参照先のカテゴリの親カテゴリはなくなります         |

# エラーハンドラ
item_api.exceptions.custom_exception_handler で定義しています。
エラーレスポンスは下記の形式です。

```commandline
{
    "message": "エラーメッセージです"
}
```

# Linter
ruff を使っています。

```commandline
brew install pre-commit
pre-commit install
```

でインストール後、

```
pre-commit run
```

を実行します。