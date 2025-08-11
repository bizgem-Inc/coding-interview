from dataclasses import dataclass
import uuid
from api.models import Category, Company


@dataclass
class CategoryListInput:
    """カテゴリ一覧取得の入力データ"""

    company: int | None = None
    parent_category: uuid.UUID | None = None
    name: str | None = None
    ordering: str = "name"
    page: int | None = None
    page_size: int | None = None

    def __init__(self, **kwargs):
        # クエリパラメータの動的処理
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


@dataclass
class CategoryDetailInput:
    """カテゴリ詳細取得の入力データ"""

    pk: uuid.UUID


@dataclass
class CategoryCreateInput:
    """カテゴリ作成の入力データ"""

    name: str
    company: Company
    parent_category: Category | None = None


@dataclass
class CategoryUpdateInput:
    """カテゴリ更新の入力データ"""

    pk: uuid.UUID
    name: str | None = None
    company: Company | None = None
    parent_category: Category | None = None


@dataclass
class CategoryDeleteInput:
    """カテゴリ削除の入力データ"""

    pk: uuid.UUID
