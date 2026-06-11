# Onion Architecture

## Architecture Principles

- Domain層にはエンティティ、NewType、純粋な業務ルールを配置する。
- Application層にはUse Case、DTO、Repositoryポートを配置する。
- Services層にはDRFによるHTTP境界を配置する。
- Repositories層にはDjango ORMモデル、Mapper、Repository実装を配置する。
- 依存関係はServices層とRepositories層からApplication層、Domain層の順に内側へ向ける。
- ViewをComposition Rootとし、RepositoryとUse Caseを組み立てる。

## Directory Structure

```text
coding-interview/
├── api/
│   ├── domain/                         # 中心: フレームワーク非依存
│   │   ├── entities/
│   │   │   ├── company.py              # Companyエンティティ
│   │   │   └── category.py             # Categoryエンティティ
│   │   ├── new_types/
│   │   │   ├── company_id.py           # CompanyId
│   │   │   └── category_id.py          # CategoryId
│   │   ├── services/                    # 複数エンティティにまたがる純粋なルール
│   │   └── exceptions.py                # ドメインルール違反
│   │
│   ├── application/                    # ユースケース
│   │   ├── ports/
│   │   │   ├── company_repository.py   # Company永続化の抽象
│   │   │   └── category_repository.py  # Category永続化の抽象
│   │   ├── dto/
│   │   │   └── category.py             # ユースケースの入出力DTO
│   │   └── use_cases/
│   │       └── category/
│   │           ├── create.py
│   │           ├── get.py
│   │           ├── list.py
│   │           ├── update.py
│   │           └── delete.py
│   │
│   ├── services/                       # 外部技術とApplication層の接続
│   │   └── web/
│   │       ├── serializers/
│   │       │   └── category.py         # DRF serializer
│   │       ├── views/
│   │       │   └── category.py         # HTTPとユースケースの接続
│   │       └── urls.py
│   │
│   ├── repositories/                   # 永続化の外層実装
│   │   └── django/
│   │       ├── company.py               # CompanyRepositoryのDjango実装
│   │       ├── category.py              # CategoryRepositoryのDjango実装
│   │       ├── orm_models/              # Django ORM専用モデル
│   │       │   ├── company.py
│   │       │   └── category.py
│   │       └── mappers/
│   │           ├── company.py           # ORMモデルとDomainの変換
│   │           └── category.py
│   │
│   ├── tests/
│   │   ├── unit/
│   │   │   ├── domain/
│   │   │   └── application/
│   │   └── integration/
│   │       ├── repositories/
│   │       └── web/
│   │
│   ├── migrations/                     # Djangoマイグレーション
│   ├── models.py                       # Djangoのモデル検出用import窓口
│   └── apps.py
│
├── config/                             # 最外周: Djangoプロジェクト設定
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── manage.py
├── Pipfile
└── Pipfile.lock
```

## Model Separation

Django ORMモデルとDomainモデルは、必ず別の型として定義する。

```text
api/domain/entities/category.py
    Category                    # 業務ルールを持つDomainエンティティ

api/repositories/django/orm_models/category.py
    CategoryModel               # テーブル定義を持つDjango ORMモデル

api/repositories/django/mappers/category.py
    to_domain(CategoryModel)    # ORMからDomainへ変換
    to_model(Category)          # DomainからORMへ変換
```

- Domainエンティティは `dataclass` などのPython標準機能で定義し、`django.db.models.Model` を継承しない。
- ORMモデルは名前に `Model` を付け、Domainエンティティとの取り違えを防ぐ。
- Domainエンティティへ `save()`、`objects`、QuerySetなどのORM APIを公開しない。
- ORMモデルに業務ユースケースを実装しない。DB制約と永続化に必要な定義だけを置く。
- RepositoryだけがMapperを使用し、ViewやUse CaseからORMモデルを直接操作しない。
- `api/models.py` はDjangoによるモデル検出のためにORMモデルをimportするだけとし、業務ロジックを置かない。

## New Types

意味の異なるプリミティブ値は、`typing.NewType` で区別する。

```python
from typing import NewType
from uuid import UUID

CompanyId = NewType("CompanyId", UUID)
CategoryId = NewType("CategoryId", UUID)
```

- NewTypeは `api/domain/new_types/` に配置する。
- IDなど、実行時検証や振る舞いを必要としない型に使用する。
- 異なるID型を同じ `UUID` として受け渡さない。
- NewTypeへ業務ロジックを持たせない。
- 実行時の値検証は、エンティティの生成処理またはUse Caseの入力境界で行う。
- `NewType` による型の区別は静的型検査に依存するため、変更後は `uv run --with pyright pyright` を必ず実行する。
- `pyright` のエラーが残る状態で変更を完了扱いにしない。

## Layer Responsibilities

### Domain

- `Company`、`Category`、NewTypeで定義したIDなどの業務概念を表現する。
- エンティティ単体の不変条件と純粋な業務ルールを保持する。
- Django、DRF、データベース、HTTPへ依存しない。
- `django.db.models.Model` やDRF Serializerをimportしない。

### Application

- 登録、取得、一覧、更新、削除の処理順序をユースケースとして定義する。
- Domain型を利用し、Repositoryポートを介して永続化を要求する。
- トランザクションなど外部機構の詳細を直接実装しない。
- HTTPステータス、Request、Response、ORM QuerySetへ依存しない。

### Services

- Web ServiceはHTTP入力をDTOへ変換し、ユースケースの結果をHTTPレスポンスへ変換する。
- Viewは具体的なRepositoryを生成し、Use Caseへ渡すComposition Rootを兼ねる。
- Viewは依存関係を組み立てた後、業務処理をUse Caseへ委譲する。
- 複数の永続化操作を行うUse Caseは、ViewでUse Case全体を `transaction.atomic()` により囲む。
- Service固有のDRF型をDomain層やApplication層へ漏らさない。
- `api/services/` はHTTPなどの外部入力との接続を担当し、業務ルールや永続化を実装しない。
- `api/domain/services/` は純粋な業務ルールを担当し、外部技術へ依存しない。

### Repositories

- `api/repositories/` はApplication層のRepositoryポートを実装する。
- Django RepositoryはORMモデルを操作し、Domainエンティティを入出力する。
- MapperはDjango ORMモデルとDomainエンティティの相互変換を担当する。
- ORM型とQuerySetをDomain層やApplication層へ漏らさない。
- 業務ルールやHTTP処理を実装しない。
- Repositoryメソッドごとにトランザクションを確定せず、呼び出し元が定義したトランザクション境界へ参加する。

## Dependency Direction

依存は必ず外側から内側へ向ける。

```text
config
   |
   v
services/web
   |       |
   |       v
   |   repositories
   |       |
   +---+---+
       |
       v
  application
       |
       v
     domain
```

Viewでの依存関係の組み立ては、次のように最小限に留める。

```python
from django.db import transaction


class CategoryViewSet(ViewSet):
    def create(self, request: Request) -> Response:
        repository = DjangoCategoryRepository()
        use_case = CreateCategory(repository)

        with transaction.atomic():
            result = use_case.execute(...)

        return Response(...)
```

独立した `infrastructure/` は設けない。依存関係の組み立てはView内に留め、業務処理はUse Caseへ委譲する。

## Transaction Boundary

- トランザクション境界はUse Case単位とする。
- Viewは、書き込みを行うUse Caseの実行全体を `transaction.atomic()` で囲む。
- 複数Repositoryを更新する場合も、すべて同じトランザクションへ参加させる。
- Repository内で独立したトランザクションを開始または確定しない。
- Domain層とApplication層はDjangoの `transaction` をimportしない。
- 読み取り専用Use Caseには、整合性要件がない限り不要なトランザクションを追加しない。

Repositoryは依存性逆転を適用する。

```text
application/ports/category_repository.py
                    ^
                    | implements
                    |
repositories/django/category.py
```

Application層はDjango Repository実装を知らず、Application層自身が定義したポートだけを参照する。

## Request Flow

Category作成APIは次の順序で処理する。

```text
HTTP Request
  -> DRF Serializer
  -> CreateCategory DTO
  -> CreateCategory Use Case
  -> Category Repository Port
  -> Django Category Repository
  -> Domain-to-ORM Mapper
  -> Django ORM Model
  -> PostgreSQL
```

取得時は `Django ORM Model -> ORM-to-Domain Mapper -> Domain Entity` の順に変換する。依存方向自体は常に内向きのままとする。

## Testing Strategy

- DomainテストはDjangoを起動せず、業務ルールと不変条件を検証する。
- ApplicationテストはインメモリRepositoryを注入し、ユースケースの意図を検証する。
- RepositoryテストはDjango ORM RepositoryとMapperを実データベースで検証する。
- Web結合テストは、Use Caseの途中で例外が発生した場合に全更新がロールバックされることを検証する。
- WebテストはHTTP契約、認証、ステータスコード、レスポンス形式を検証する。
- 同じ振る舞いを全層で重複してテストせず、各層の責務に対応する意図を検証する。
