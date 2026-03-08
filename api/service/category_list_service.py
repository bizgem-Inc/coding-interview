import uuid

from api.repository import CategoryRepository


class CategoryListService:

    def __init__(self, category_repository: CategoryRepository):
        self.category_repository = category_repository

    def handle(self, company_id: uuid):
        return self.category_repository.find_by_company_id(company_id)
