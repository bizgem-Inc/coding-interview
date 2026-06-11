from typing import Optional

from api.domain.entities.company import Company
from api.domain.new_types.company_id import CompanyId
from api.repositories.django.mappers.company import to_domain
from api.repositories.django.orm_models.company import CompanyModel


class DjangoCompanyRepository:
    """CompanyのDjango ORM実装。"""

    def find_by_id(self, company_id: CompanyId) -> Optional[Company]:
        try:
            model = CompanyModel.objects.get(id=company_id)
        except CompanyModel.DoesNotExist:
            return None
        return to_domain(model)
