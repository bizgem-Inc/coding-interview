import uuid

from api.repository import CategoryRepository


class CategoryRetrieveService:

    def __init__(self, category_repository: CategoryRepository):
        self.category_repository = category_repository

    def handle(self, company_id: uuid.UUID, category_id: uuid.UUID):
        return self.category_repository.find(company_id, category_id)
