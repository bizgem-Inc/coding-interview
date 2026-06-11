---
id: category-crud-api
title: Category CRUD API
status: completed
owner: Codex
updated_at: 2026-06-11
next_action: 完了
file: docs/plans/2026-06-11_category-crud-api.md
---

## 目的

Categoryの一覧取得、詳細取得、作成、更新、削除をHTTP APIとして提供し、各操作の契約を自動テストで保証する。

## スコープ

- 対象: Category CRUD API、入力・出力Serializer、CategoryのDomainモデル、Use Case、Repositoryポート、Django Repository、Mapper、URL登録、APIテスト
- 対象外: Company CRUD API、認証・認可、ページネーション、検索・並び替え、論理削除、親カテゴリと子カテゴリの循環検証、親カテゴリが同一企業に属する制約の追加

## 重要要件

- `GET /api/categories/` でCategory一覧を取得できる。
- `GET /api/categories/{category_id}/` でCategory詳細を取得できる。
- `POST /api/categories/` でCategoryを作成できる。
- `PUT` と `PATCH /api/categories/{category_id}/` でCategoryを更新できる。
- `DELETE /api/categories/{category_id}/` でCategoryを削除できる。
- 存在しないCategoryの詳細取得、更新、削除は404を返す。
- 存在しないCompanyまたは親Categoryを指定した作成・更新は400を返す。
- 同一Company内で重複するCategory名の作成・更新は400を返す。
- 書き込み操作はUse Case単位のトランザクション内で実行する。
- Django ORMモデルとDomainモデルを分離し、Mapperを介して変換する。

## API契約

- 一覧・詳細レスポンス項目: `id`, `company_id`, `name`, `parent_category_id`, `created_at`, `updated_at`
- 作成入力: `company_id`, `name`, `parent_category_id`
- 更新入力: `company_id`, `name`, `parent_category_id`
- `parent_category_id` は省略または `null` を許可する。
- 作成成功は201、一覧・詳細・更新成功は200、削除成功は204とする。
- UUID形式不正、必須項目不足、255文字を超える名前は400とする。
- 認証は要求しない。

入力例:

```json
{
  "company_id": "11111111-1111-1111-1111-111111111111",
  "name": "Backend",
  "parent_category_id": null
}
```

## 画面遷移

- 対象外。HTTP APIのみを実装する。

## 変更対象

- Domain: `api/domain/entities/category.py`, `api/domain/new_types/category_id.py`, `api/domain/new_types/company_id.py`
- Application: `api/application/dto/category.py`, `api/application/ports/category_repository.py`, `api/application/use_cases/category/`
- Repositories: `api/repositories/django/category.py`, `api/repositories/django/orm_models/`, `api/repositories/django/mappers/category.py`
- Services: `api/services/web/serializers/category.py`, `api/services/web/views/category.py`, `api/services/web/urls.py`
- Django連携: `api/models.py`, `api/urls.py`, `api/migrations/`
- Tests: `api/tests/unit/`, `api/tests/integration/repositories/`, `api/tests/integration/web/test_category.py`
- 既存の `api/views/category.py`, `api/serializers/category.py`, `api/tests/test_views.py` は移行完了後に不要な空ファイルを削除する。

## タスク

1. API契約をWebテストで固定する
- 成果物: 一覧、詳細、作成、PUT/PATCH更新、削除、404、400の失敗するテスト
- テスト: `api/tests/integration/web/test_category.py`

2. Domain型とNewTypeを定義する
- 成果物: Django非依存のCategoryエンティティ、`CategoryId`、`CompanyId`
- テスト: Categoryの生成とフィールド保持を検証するDomain単体テスト

3. Application層の契約を定義する
- 成果物: Category DTO、Repositoryポート、一覧・詳細・作成・更新・削除Use Case
- テスト: インメモリRepositoryを用いた各Use Caseの単体テスト

4. Django RepositoryとMapperを実装する
- 成果物: ORMモデル、Domain変換Mapper、RepositoryポートのDjango実装、Djangoモデル検出用import、マイグレーション
- テスト: 保存、取得、一覧、更新、削除、存在しないID、重複制約を検証するRepository結合テスト

5. SerializerとViewを実装する
- 成果物: 入力検証Serializer、出力Serializer、Category ViewSet
- テスト: タスク1で追加したWebテストを通過させる
- 補足: ViewでRepositoryとUse Caseを組み立て、作成・更新・削除を `transaction.atomic()` で囲む

6. URLを登録する
- 成果物: `/api/categories/` と `/api/categories/{category_id}/` のルーティング
- テスト: 名前付きURLのreverseと各HTTPメソッドの到達性をWebテストで検証する

7. 旧配置を整理する
- 成果物: 置き換え済みの空ファイルと古いimportを削除し、アーキテクチャ記載の配置へ統一する
- テスト: importエラーがなく、全テストと型検査が通ることを確認する

8. 全体検証を行う
- 成果物: マイグレーション差分なし、型エラーなし、全テスト成功
- テスト: `uv run python manage.py makemigrations --check --dry-run`, `uv run --with pyright pyright`, `uv run python manage.py test`

## 要件と自動テストの対応

- Category一覧を取得できる -> `CategoryViewTests.test_list`
- Category詳細を取得できる -> `CategoryViewTests.test_retrieve`
- Categoryを作成できる -> `CategoryViewTests.test_create`
- CategoryをPUT更新できる -> `CategoryViewTests.test_update`
- CategoryをPATCH更新できる -> `CategoryViewTests.test_partial_update`
- Categoryを削除できる -> `CategoryViewTests.test_destroy`
- 存在しないCategoryが404になる -> `CategoryViewTests.test_missing_category_returns_404`
- 存在しないCompanyが400になる -> `CategoryViewTests.test_create_with_missing_company_returns_400`
- 存在しない親Categoryが400になる -> `CategoryViewTests.test_create_with_missing_parent_returns_400`
- 同一Company内の名前重複が400になる -> `CategoryViewTests.test_duplicate_name_in_company_returns_400`
- 入力形式不正が400になる -> `CategoryViewTests.test_invalid_payload_returns_400`
- 書き込みが原子的に処理される -> `CategoryViewTests.test_write_rolls_back_when_use_case_fails`
- ORMとDomainがMapper経由で変換される -> `CategoryMapperTests`
- Use CaseがRepositoryポートだけに依存する -> `CreateCategoryTests`, `UpdateCategoryTests`, `DeleteCategoryTests`

## テスト観点

- 正常系: すべてのCRUD操作、親なし・親ありCategory、PUTとPATCHの差
- 入力境界: UUID形式、必須項目、`null`、名前長
- 参照整合性: Companyと親Categoryの存在確認
- 一意制約: 同一Companyでは重複不可、異なるCompanyでは同名を許可
- HTTP契約: ステータスコード、レスポンス項目、削除後の404
- 層境界: Domain/ApplicationがDjangoとDRFをimportしない
- 永続化: Mapperの往復変換とRepositoryのCRUD
- トランザクション: Use Case失敗時のロールバック

## 受け入れ条件

- `/api/categories/` がGETとPOSTを受け付ける。
- `/api/categories/{category_id}/` がGET、PUT、PATCH、DELETEを受け付ける。
- 成功時のステータスコードとレスポンス項目がAPI契約どおりである。
- 不正入力、参照先不存在、同一Company内の名前重複が400になる。
- 対象Category不存在が404になる。
- Django ORMモデルとDomainモデルが別クラスであり、Repository Mapperを介して変換される。
- Domain層とApplication層がDjangoおよびDRFへ依存しない。
- 書き込みUse Caseがトランザクション内で実行される。
- `uv run python manage.py makemigrations --check --dry-run` が成功する。
- `uv run --with pyright pyright` が0エラーで終了する。
- `uv run python manage.py test` がスキップなしで成功する。

## 前提・判断

- ユーザー指定の `views/category.py` と `test_views.py` は実装イメージとして扱い、最終配置は `ARCHITECTURE.md` を優先する。
- CategoryのDB仕様は既存のUUID主キー、Company外部キー、任意の親Category、同一Company内の名前一意制約を維持する。
- 親Categoryが同じCompanyに属することは既存モデルで保証されていないため、今回新たな業務制約として追加しない。
- 一覧のページネーションと順序保証は要求されていないため追加しない。
- CompanyはテストFixtureまたはORMで事前作成し、Company APIは追加しない。
