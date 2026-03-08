import uuid

from rest_framework.exceptions import NotFound

from api.repository import CategoryRepository


class CategoryDestroyService:

    def __init__(self, category_repository: CategoryRepository):
        self.category_repository = category_repository

    def handle(self, company_id: uuid, category_id: uuid):
        category =  self.category_repository.find(company_id, category_id)

        if category is None:
            raise NotFound("Category not found")

        return self.category_repository.delete(category)
