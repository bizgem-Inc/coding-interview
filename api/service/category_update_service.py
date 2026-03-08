import uuid

from rest_framework.exceptions import NotFound, ValidationError

from api.repository import CategoryRepository


class CategoryUpdateService:

    def __init__(self, category_repository: CategoryRepository):
        self.category_repository = category_repository

    def handle(self, company_id: uuid.UUID, category_id: uuid.UUID, name: str, parent_category_id: uuid.UUID | None,):

        if not self.category_repository.find(company_id, category_id):
            raise NotFound("Category not found")

        if category_id == parent_category_id:
            raise ValidationError("Category cannot be its own parent")

        if parent_category_id is not None:
            parent_category = self.category_repository.find(company_id, parent_category_id)

            if parent_category is None:
                raise NotFound("Parent category not found")

            if self.category_repository.is_descendant(category_id, parent_category_id):
                raise ValidationError("Cycle detected")

        if not self.category_repository.is_unique(company_id, name, category_id):
            raise ValidationError("Category name already exists")

        return self.category_repository.update(category_id, name, parent_category_id)
