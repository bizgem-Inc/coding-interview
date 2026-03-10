import uuid

from rest_framework.exceptions import NotFound, ValidationError

from api.repository import CategoryRepository
from api.repository.company_repository import CompanyRepository


class CategoryDestroyService:

    def __init__(self, category_repository: CategoryRepository, company_repository: CompanyRepository):
        self.category_repository = category_repository
        self.company_repository = company_repository

    def handle(self, company_id: uuid.UUID, category_id: uuid.UUID):
        company = self.company_repository.get_by_id(company_id)
        category =  self.category_repository.get(company.id, category_id)

        if self.category_repository.has_children(category.id):
            raise ValidationError({"detail": "Category has child categories"})

        return self.category_repository.delete(category.id)
