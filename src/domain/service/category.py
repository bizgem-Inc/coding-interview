from inject import autoparams
from domain.repository.category import ICategoryRepository
from domain.entity.category import CategoryEntity
from domain.entity.company import CompanyEntity
from uuid import UUID
from typing import Optional
from api.base import ResourceNotFoundException

class CategoryDomainService:
    @autoparams("category_repository")
    def __init__(self, category_repository: ICategoryRepository):
        self.category_repository = category_repository

    def fetch(self, id):
        return self.category_repository.fetch(id)

    def list_all(self):
        return self.category_repository.list_all()

    def create(
            self,
            name: str,
            parent_category_id: Optional[UUID],
            company_name: str
        ) -> CategoryEntity:
        parent_category = None
        if parent_category_id is not None:
            parent_category = self.category_repository.fetch(parent_category_id)

        company = CompanyEntity.new(company_name)

        category = CategoryEntity.new(
            name=name,
            company=company,
            parent_category=parent_category
        )

        return self.category_repository.create(category)

    def update(
            self,
            id: str,
            name: str,
            parent_category_id: Optional[UUID],
            company_name: str
        ):

        category = self.category_repository.fetch(id)

        if category is None:
            raise ResourceNotFoundException

        # 項目が増えるならエンティティ側にバルク更新メソッドを定義したい
        if name is not None:
            category.change_name(name)

        if parent_category_id is not None:
            parent_category = self.category_repository.fetch(parent_category_id)
            category.change_parent_category(parent_category)

        if company_name is not None:
            category.change_company(company_name)

        self.category_repository.update(category)

    def delete(self, id):
        self.category_repository.delete(id)
