from typing import Optional

from api.application.ports.category_repository import CategoryRepository
from api.domain.entities.category import Category
from api.domain.new_types.category_id import CategoryId
from api.domain.new_types.company_id import CompanyId
from api.repositories.django.mappers.category import to_domain, to_model
from api.repositories.django.orm_models.category import CategoryModel
from api.repositories.django.orm_models.company import CompanyModel


class DjangoCategoryRepository:
    """CategoryRepositoryのDjango ORM実装。"""

    def find_by_id(self, category_id: CategoryId) -> Optional[Category]:
        try:
            model = CategoryModel.objects.get(id=category_id)
        except CategoryModel.DoesNotExist:
            return None
        return to_domain(model)

    def find_all(self, limit: int = 10, offset: int = 0) -> list[Category]:
        models = CategoryModel.objects.all().order_by("id")
        return [to_domain(m) for m in models[offset : offset + limit]]

    def save(self, category: Category) -> Category:
        company = CompanyModel.objects.get(id=category.company_id)
        parent = (
            CategoryModel.objects.get(id=category.parent_category_id)
            if category.parent_category_id
            else None
        )
        # 既存レコードを更新、なければ新規作成
        obj, _ = CategoryModel.objects.update_or_create(
            id=category.id,
            defaults={
                "company": company,
                "name": category.name,
                "parent_category": parent,
                "created_at": category.created_at,
                "updated_at": category.updated_at,
            },
        )
        return to_domain(obj)

    def delete(self, category_id: CategoryId) -> None:
        CategoryModel.objects.filter(id=category_id).delete()

    def find_by_company_and_name(
        self, company_id: CompanyId, name: str
    ) -> Optional[Category]:
        try:
            model = CategoryModel.objects.get(
                company_id=company_id, name=name
            )
        except CategoryModel.DoesNotExist:
            return None
        return to_domain(model)

    def find_parent_by_id(
        self, parent_category_id: CategoryId
    ) -> Optional[Category]:
        try:
            model = CategoryModel.objects.get(id=parent_category_id)
        except CategoryModel.DoesNotExist:
            return None
        return to_domain(model)

    def company_exists(self, company_id: CompanyId) -> bool:
        return CompanyModel.objects.filter(id=company_id).exists()
