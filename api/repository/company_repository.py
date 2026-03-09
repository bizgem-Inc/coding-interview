import uuid

from api.models import Company


class CompanyRepository:

    def get_by_id(self, company_id: uuid.UUID):
        return Company.objects.get(id = company_id)
