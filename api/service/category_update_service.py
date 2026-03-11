import uuid

from rest_framework.exceptions import NotFound, ValidationError

from api.repository import CategoryRepository, CompanyRepository


class CategoryUpdateService:

    def __init__(self, category_repository: CategoryRepository, company_repository: CompanyRepository):
        self.category_repository = category_repository
        self.company_repository = company_repository

    def handle(self, company_id: uuid.UUID, category_id: uuid.UUID, name: str, parent_category_id: uuid.UUID | None,):

        company_id = self.company_repository.get_by_id(company_id).id

        if not self.category_repository.find(company_id, category_id):
            raise NotFound("Category not found")

        if category_id == parent_category_id:
            raise ValidationError({"detail": "Category cannot be its own parent"})

        if parent_category_id is not None:
            parent_category = self.category_repository.find(company_id, parent_category_id)

            if parent_category is None:
                raise NotFound("Parent category not found")

            if self.category_repository.would_create_cycle(category_id, parent_category_id):
                raise ValidationError({"detail": "Cycle detected"})

        if not self.category_repository.is_unique(company_id, name, category_id):
            raise ValidationError({"detail": "Category name already exists"})

        return self.category_repository.update(category_id, name, parent_category_id)
