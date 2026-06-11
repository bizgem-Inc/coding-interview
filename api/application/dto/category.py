from dataclasses import dataclass
from typing import Optional

from api.domain.new_types.category_id import CategoryId
from api.domain.new_types.company_id import CompanyId


@dataclass(frozen=True)
class CreateCategoryRequest:
    company_id: CompanyId
    name: str
    parent_category_id: Optional[CategoryId]


@dataclass(frozen=True)
class UpdateCategoryRequest:
    company_id: CompanyId
    name: str
    parent_category_id: Optional[CategoryId]


@dataclass(frozen=True)
class CategoryResponse:
    id: CategoryId
    company_id: CompanyId
    name: str
    parent_category_id: Optional[CategoryId]
    created_at: "datetime"
    updated_at: "datetime"


# datetimeの循環importを避けるために遅延評価
from datetime import datetime  # noqa: E402
