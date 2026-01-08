## 概要

本リポジトリは、Category モデルに対する CRUD API を
Django REST Framework を用いて実装したものです。

認証・認可は考慮せず、
API の設計、バリデーション、テストの実装を重視しています。

---

## 実装方針

### API 実装

- Django REST Framework の `ModelViewSet` を使用
- CRUD 処理はフレームワーク標準に委譲し、
  独自ロジックは Serializer に集約しています

### バリデーション

以下の業務ルールを Serializer で検証しています。

- カテゴリ名は必須（空文字・空白のみは不可）
- 同一企業（company）内ではカテゴリ名は一意
- 親カテゴリ（parent_category）は同一企業に属している必要がある

DB 制約ではなく Serializer 側で検証することで、
API レイヤーで明示的なエラーレスポンスを返す設計としています。

---

## 削除時の挙動について

`parent_category` は `on_delete=models.SET_NULL` として定義されています。

そのため、

- 親カテゴリ削除時
  - 親カテゴリ：削除される
  - 子カテゴリ：削除されず残る
  - 子カテゴリの parent_category：NULL になる

という挙動になります。

この仕様はテストコードで明示的に検証しています。

---

## テストについて

- Django REST Framework の `APITestCase` を使用
- API レベルで以下を検証しています
  - CRUD の正常系
  - 各種バリデーションの異常系
  - 親子関係を持つカテゴリ削除時の挙動

テストは実装したバリデーション仕様をすべて網羅することを
目的としています。

---

## テスト実行方法

```bash
python manage.py test
