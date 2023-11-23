# coding-interview

# 実装・テストの作業報告

## 環境構築 <2023/11/15～2023/11/16>
1. 実行環境 : WSL2 Ubuntu22
2. DB      : postgres16.1をインストール(公式のdockerコンテナーイメージを使用)
3. python3 : 3.11.6を追加インストール
4. pip     : 23.3.1を追加インストール
5. venv    : python3.11-venvを追加インストール
6. pgAdmin4: 7.8をインストール

## coding-interviewセットアップ (2023/11/17)
1. gitクローンでソースを取得
2. requirements.txtがなく、代わりにPipfile、Pipfile.lockを発見。名前からnode.jsのnpmと同様の用途であることを把握。「pip install pipenv」でインストール後、「pipenv sync --dev」によりPipfile.lockよりインストールを実施。
3. 初回マイグレートを実施⇒　エラー　⇒　psycopg2-binaryが不足していたため「pip install psycopg2-binary」により追加インストール　⇒　マイグレート成功
   - ※pipenv update psycopg2-binaryとpipfileをカスタマイズすることでpipenvでインストール可能であるが、自身以外の環境への影響が出てしまう恐れがある。他者の環境では「psycopg2」でインストール可能の場合もあるためPipfile、Pipfile.lockを更新することは許可なく進めるべきではないと判断。そのため自環境用にpip installを用いてインストールを実施。
4. 最終的に以下の環境にて開発を実施
```
    (.venv) :coding-interview$ pip freeze  
    asgiref==3.7.2  
    certifi==2023.7.22  
    distlib==0.3.7  
    Django==4.2.4  
    djangorestframework==3.14.0  
    filelock==3.13.1  
    pipenv==2023.11.15  
    platformdirs==3.11.0  
    psycopg2-binary==2.9.9  
    pytz==2023.3  
    sqlparse==0.4.4  
    virtualenv==20.24.6  
```

## Djangoの復習、Django Rest FrameWorkの使用方法修得 (2023/11/18～2023/11/19)
1. Djangoを過去に使ったバージョンは2.0であり、今回4.2を使うこととなったため改めて復習兼習得を実施。
2. Django Rest FrameWorkは未習得であったため、今回の要件に関わるところのみターゲットを絞って習得。「viewsets.ModelViewSet」を使用してモデルに対するapiの構築ができることを発見。
3. 「viewsets.ModelViewSet」はブラウザーからアクセスした場合、htmlで検証しやすい形式でレスポンスを返してくるが、「crul」コマンドや「Chromeブラウザー・拡張機能・Talend API Tester」などを使った場合、json形式でデータのみ返す機能を持つことを理解。

## 実装＆テスト (2023/11/20～2023/11/23)
1. urls、view、serializers実装およびテストを実施。
2. 以下テストの実行ログ証跡。
```
(.venv) :coding-interview$ python manage.py test api
Found 6 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
......
----------------------------------------------------------------------
Ran 6 tests in 0.317s

OK
Destroying test database for alias 'default'...
(.venv) :coding-interview$ 
```

## その他 
1. adminの実装は一度行いましたが、セキュリティ上使用しない運用としている可能性もあり、要件にもありませんでしたので削除してあります。
2. companyのviewの実装は今回の要件になかったため見送っております。
3. テストの実装時、データファクトリーは必要とするほどのテストではなかったため使用は見送っております。
