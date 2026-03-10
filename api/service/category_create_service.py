import uuid

from rest_framework.exceptions import NotFound, ValidationError

from api.repository import CategoryRepository
from api.repository.company_repository import CompanyRepository


class CategoryCreateService:

    def __init__(self, category_repository: CategoryRepository, company_repository: CompanyRepository):
        self.category_repository = category_repository
        self.company_repository = company_repository

    def handle(self, company_id: uuid.UUID, name: str, parent_category_id: uuid.UUID | None,):

        company = self.company_repository.get_by_id(company_id)

        if parent_category_id is not None:
            # 親カテゴリーが存在しない場合はエラーを返す
            self.category_repository.get(company.id, parent_category_id)

        if not self.category_repository.is_unique(company.id, name):
            raise ValidationError({"detail": "Category name already exists"})

        return self.category_repository.create(company.id, name, parent_category_id)
