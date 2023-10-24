from typing import List
from uuid import UUID
from django.core.exceptions import ObjectDoesNotExist

from domain.entity.category import CategoryEntity
from domain.entity.company import CompanyEntity
from domain.repository.category import ICategoryRepository
from infrastructure.models.category import Category
from infrastructure.models.company import Company


class CategoryRepository(ICategoryRepository):
    def fetch(self, id: UUID) -> CategoryEntity:
        try:
            category = Category.objects.get(id=id)
        except ObjectDoesNotExist:
            return None

        return CategoryEntity.from_record(
            id=category.id,
            company=CompanyEntity.from_record(
                id=category.company.id,
                name=category.company.name,
                created_at=category.company.created_at,
                updated_at=category.company.updated_at,
            ),
            name=category.name,
            parent_category=category.parent_category,
            created_at=category.created_at,
            updated_at=category.updated_at,
        )

    def list_all(self) -> List[CategoryEntity]:
        categories = Category.objects.all()
        result = []
        for category in categories:
            result.append(
                CategoryEntity.from_record(
                id=category.id,
                company=CompanyEntity.from_record(
                    id=category.company.id,
                    name=category.company.name,
                    created_at=category.company.created_at,
                    updated_at=category.company.updated_at,
                ),
                name=category.name,
                parent_category=category.parent_category,
                created_at=category.created_at,
                updated_at=category.updated_at,
            )
            )
        return result

    def create(self, category: CategoryEntity) -> CategoryEntity:
        company, _created = Company.objects.get_or_create(
            id=category.company.id,
            defaults={'name': category.company.name}
        )

        new_category = Category.objects.create(
            company=company,
            name=category.name,
            parent_category=category.parent_category
        )

        return CategoryEntity.from_record(
            id=new_category.id,
            company=CompanyEntity.from_record(
                id=new_category.company.id,
                name=new_category.company.name,
                created_at=new_category.company.created_at,
                updated_at=new_category.company.updated_at,
            ),
            name=new_category.name,
            parent_category=new_category.parent_category,
            created_at=new_category.created_at,
            updated_at=new_category.updated_at,
        )

    def update(self, category: CategoryEntity):
        Category.objects.filter(id=category.id).update(
            company=category.company.id,
            name=category.name,
            parent_category=category.parent_category,
            updated_at=category.updated_at
        )

    def delete(self, id: UUID):
        Category.objects.filter(id=id).delete()
