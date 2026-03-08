import uuid

from rest_framework.exceptions import NotFound, ValidationError

from api.repository import CategoryRepository, CompanyRepository


class CategoryCreateService:

    def __init__(self, category_repository: CategoryRepository):
        self.category_repository = category_repository

    def handle(self, company_id: uuid.UUID, name: str, parent_category_id: uuid.UUID | None,):

        if parent_category_id is not None:
            parent_category = self.category_repository.find(company_id, parent_category_id)

            if parent_category is None:
                raise NotFound("Parent category not found")

        if not self.category_repository.is_unique(company_id, name):
            raise ValidationError("Category name already exists")

        return self.category_repository.create(company_id, name, parent_category_id)
