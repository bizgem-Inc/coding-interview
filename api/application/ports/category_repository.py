from typing import Optional, Protocol

from api.domain.entities.category import Category
from api.domain.new_types.category_id import CategoryId
from api.domain.new_types.company_id import CompanyId


class CategoryRepository(Protocol):
    """Category永続化の抽象ポート。"""

    def find_by_id(self, category_id: CategoryId) -> Optional[Category]:
        """IDでCategoryを取得する。"""
        ...

    def find_all(self, limit: int = 10, offset: int = 0) -> list[Category]:
        """Categoryを取得する。limit指定でページネーション。"""
        ...

    def save(self, category: Category) -> Category:
        """Categoryを保存する。"""
        ...

    def delete(self, category_id: CategoryId) -> None:
        """Categoryを削除する。"""
        ...

    def find_by_company_and_name(
        self, company_id: CompanyId, name: str
    ) -> Optional[Category]:
        """企業と名前でCategoryを検索する。"""
        ...

    def find_parent_by_id(self, parent_category_id: CategoryId) -> Optional[Category]:
        """親Categoryが存在するか確認する。"""
        ...

    def company_exists(self, company_id: CompanyId) -> bool:
        """企業が存在するか確認する。"""
        ...
