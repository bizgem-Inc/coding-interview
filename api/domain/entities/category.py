from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from api.domain.new_types.category_id import CategoryId
from api.domain.new_types.company_id import CompanyId


@dataclass(frozen=True)
class Category:
    id: CategoryId
    company_id: CompanyId
    name: str
    parent_category_id: Optional[CategoryId]
    created_at: datetime
    updated_at: datetime
