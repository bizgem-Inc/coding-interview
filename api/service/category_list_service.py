import uuid

from api.repository import CategoryRepository, CompanyRepository


class CategoryListService:

    def __init__(self, category_repository: CategoryRepository, company_repository: CompanyRepository):
        self.category_repository = category_repository
        self.company_repository = company_repository

    def handle(self, company_id: uuid.UUID):

        company = self.company_repository.get_by_id(company_id)
        return self.category_repository.find_by_company_id(company.id)
