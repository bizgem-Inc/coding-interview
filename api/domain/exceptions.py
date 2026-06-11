from __future__ import annotations

from api.domain.new_types.category_id import CategoryId
from api.domain.new_types.company_id import CompanyId


class DomainError(Exception):
    """ドメインルール違反の基底例外。"""


class CompanyNotFoundError(DomainError):
    """指定された企業が見つからない。"""

    def __init__(self, company_id: CompanyId) -> None:
        self.company_id = company_id
        super().__init__(f"Company not found: {company_id}")


class CategoryNotFoundError(DomainError):
    """指定されたカテゴリが見つからない。"""

    def __init__(self, category_id: CategoryId) -> None:
        self.category_id = category_id
        super().__init__(f"Category not found: {category_id}")


class DuplicateCategoryNameError(DomainError):
    """同一企業内で重複するカテゴリ名。"""

    def __init__(self, name: str, company_id: CompanyId) -> None:
        self.name = name
        self.company_id = company_id
        super().__init__(f"Duplicate category name '{name}' in company {company_id}")


class ReferencedCategoryNotFoundError(DomainError):
    """参照先のCategoryが存在しない（親Categoryなど）。"""

    def __init__(self, category_id: CategoryId) -> None:
        self.category_id = category_id
        super().__init__(f"Referenced category not found: {category_id}")
