from dataclasses import dataclass
from datetime import datetime

from api.domain.new_types.company_id import CompanyId


@dataclass(frozen=True)
class Company:
    id: CompanyId
    name: str
    created_at: datetime
    updated_at: datetime
