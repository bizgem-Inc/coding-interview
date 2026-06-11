# api/AGENTS.md

# Python Soundness Rules for LLMs

Pythonコードを生成、修正、レビューするLLM向けの規則である。
目的は、Rustの設計思想を参考に、APIの誤用と不正な状態を可能な限り型と構造で防ぐことである。

出典:
https://kobzol.github.io/rust/python/2023/05/20/writing-python-like-its-rust.html

## Core Principle

- 不正な状態を表現できない設計を優先する。
- 実行時の注意書きや呼び出し規約より、型検査で誤用を検出できるAPIを優先する。
- 型はドキュメントの代用品ではなく、呼び出し側と実装側の契約として扱う。
- Pythonの動的性質を理由に型を省略しない。ただし、型を正確にするためだけの過度な複雑化は避ける。

## Type Hints

- 公開関数とメソッドの引数、戻り値、クラス属性には型注釈を付ける。
- `Any` は外部ライブラリとの境界など、型を具体化できない理由がある場合だけ使用する。
- `Optional[T]` または `T | None` を使い、値が存在しない可能性を明示する。
- コールバックには `Callable`、構造的インターフェースには必要に応じて `Protocol` を使用する。
- 複雑すぎる型が必要になった場合は、そのまま巨大な型注釈を書く前にAPIやデータ構造を単純化できないか検討する。
- 型注釈を追加しただけで完了とせず、プロジェクトで採用している型チェッカーを実行する。

## Structured Data

- 意味の異なる複数の値を、位置依存のタプルとして返さない。
- 固定された構造を持つデータを `dict[str, Any]` で受け渡さない。
- 名前付きフィールドを持つ値には、原則として `dataclass` または既存のドメインクラスを使用する。
- 辞書形式が必要な外部境界では、内部の型付きモデルと外部DTOを分離する。
- `TypedDict` は辞書形式そのものが契約である場合に使用する。
- `NamedTuple` は不変かつタプル互換である必要がある場合に使用する。
- 新しいクラスを作る前に、同じ概念を表す既存型がないか検索する。

## Closed Variants

- 取り得る種類が有限であるデータは、各種類を個別の型として定義し、Union型でまとめる。
- 各バリアント固有のフィールドを、巨大なクラスの多数の `None` 属性で表現しない。
- 閉じた種類の分岐には `match` または明示的な `isinstance` 分岐を使用する。
- 全バリアントを処理し、到達不能な分岐には `typing.assert_never` を使用する。
- 到達不能性の保証に `assert False` を使用しない。`assert` は最適化実行時に削除される。
- 種類の追加時に型チェッカーが未処理の分岐を検出できる構造を維持する。

例:

```python
from dataclasses import dataclass
from typing import assert_never


@dataclass(frozen=True)
class Header:
    size: int


@dataclass(frozen=True)
class Payload:
    data: bytes


Packet = Header | Payload


def packet_size(packet: Packet) -> int:
    match packet:
        case Header(size=size):
            return size
        case Payload(data=data):
            return len(data)
        case _:
            assert_never(packet)
```

## Domain-Specific Primitive Types

- 同じ基底型でも意味が異なる値を、そのまま混用しない。
- ID、単位、正規化状態など、取り違えがバグになる値には `NewType` または専用クラスを使用する。
- 値の検証や振る舞いが不要なら `NewType` を優先する。
- 実行時検証、不変条件、変換処理が必要なら専用の `dataclass` または値オブジェクトを使用する。
- 型安全性を失う無条件なキャストで、異なるドメイン型を相互変換しない。

例:

```python
from typing import NewType

CarId = NewType("CarId", int)
DriverId = NewType("DriverId", int)


def get_ride(car_id: CarId, driver_id: DriverId) -> None:
    ...
```

## Construction

- 1つの `__init__` に相互排他的な初期化方法を詰め込まない。
- 構築方法が複数ある場合は、目的が分かる名前付きコンストラクタを使用する。
- 構築完了後のオブジェクトが不変条件を満たすようにする。
- 一部だけ初期化されたオブジェクトを作り、後から必須メソッドを順番に呼ばせる設計を避ける。
- 検証に失敗した場合は、プロジェクトの規約に従って明示的な例外または型付きの失敗結果を返す。

例:

```python
@dataclass(frozen=True)
class Rectangle:
    left: float
    top: float
    width: float
    height: float

    @classmethod
    def from_corners(
        cls,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
    ) -> "Rectangle":
        return cls(x1, y1, x2 - x1, y2 - y1)
```

## State Transitions

- 相互排他的なライフサイクル状態を、1つのクラスのフラグ群で管理しない。
- 状態ごとに利用可能な操作が異なる場合は、状態ごとに型を分ける。
- メソッド呼び出し順をコメントだけで要求しない。
- 遷移メソッドは次の状態を表す型を返す。
- 無効な状態では、その操作をメソッドとして公開しない。
- リソースの解放には、手動の `close()` 呼び出しだけに依存せず、可能ならコンテキストマネージャーを使用する。

例:

```python
class ConnectedClient:
    def authenticate(self, password: str) -> "AuthenticatedClient":
        ...


class AuthenticatedClient:
    def send_message(self, message: str) -> None:
        ...
```

## Invariants and Representations

- 同じ形でも不変条件が異なる値は、別の型として表現する。
- 正規化済みと未正規化、検証済みと未検証、暗号化済みと平文などを同じ型で表さない。
- 不変条件は生成時に検証し、不正なインスタンスを作らせない。
- 表現間の変換は、名前付きの明示的な関数またはメソッドで行う。
- 共通処理が必要な場合のみ、合成、基底クラス、`Protocol` のいずれかを既存設計に合わせて使用する。
- 派生型を保持して返す共通メソッドには、必要に応じて `typing.Self` を使用する。

## Resource and Lock Safety

- ロックは原則として `with` 文で取得し、確実に解放する。
- `acquire()` と `release()` を離れた場所で手動管理しない。
- 共有データと、そのデータを保護するロックを同じ所有オブジェクトにまとめる。
- 保護対象へロックなしでアクセスできる公開経路を作らない。
- ファイル、接続、トランザクションなど、スコープ終了時に解放すべき資源にはコンテキストマネージャーを使用する。

## Review Checklist

コードを生成または変更した後、次を確認する。

- 関数シグネチャだけで、必要な入力と戻り値を理解できるか。
- タプル、汎用辞書、`Any` がドメイン型を隠していないか。
- 引数の入れ替えや単位の混同を型で防げるか。
- 不正な状態や無効な操作順を構築できてしまわないか。
- Union型の全バリアントを処理しているか。
- リソース解放やロック解除を呼び出し側の注意力だけに依存していないか。
- 実行時チェックを、より早く検出できる型設計へ移せないか。
- 型安全性のために、要求以上の抽象化や複雑さを追加していないか。

## Priority

規則が競合する場合は、次の順序で判断する。

1. 正しさと不変条件の維持
2. 既存コードベースの規約との整合
3. 型チェッカーによる誤用の早期検出
4. APIの明確さ
5. 実装の簡潔さ

型による厳密さが著しく複雑な設計を生む場合は、最も単純で理解可能な型を選び、残る制約をテストと明示的な実行時検証で補う。
