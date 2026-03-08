import uuid

from rest_framework.exceptions import NotFound, ValidationError

from api.repository import CategoryRepository


class CategoryDestroyService:

    def __init__(self, category_repository: CategoryRepository):
        self.category_repository = category_repository

    def handle(self, company_id: uuid.UUID, category_id: uuid.UUID):
        category =  self.category_repository.find(company_id, category_id)

        if category is None:
            raise NotFound("Category not found")

        if self.category_repository.has_children(category.id):
            raise ValidationError("Category has child categories")

        return self.category_repository.delete(category.id)
