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
poetry install
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

# API の実行
Company と Category があります。

## Company
非常にシンプルな CRUD です。
Category が存在する Company は削除できません。

```commandline
/api/companies
```