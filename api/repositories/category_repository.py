from uuid import UUID
from api.models.category import Category
from django.db.models import QuerySet


class CategoryRepository:
    def get_categories(self, company_id: UUID) -> QuerySet[Category]:
        return Category.objects.filter(company_id=company_id)

    def get_category_by_id(self, category_id: UUID) -> Category:
        return Category.objects.get(id=category_id)

    def create_category(
        self, company_id: UUID, name: str, parent_category_id: UUID | None = None
    ) -> Category:
        return Category.objects.create(
            company_id=company_id, name=name, parent_category_id=parent_category_id
        )

    def update_category(self, category_id: UUID, **kwargs) -> None:
        Category.objects.filter(id=category_id).update(**kwargs)

    def delete_category(self, category_id: UUID) -> None:
        Category.objects.filter(id=category_id).delete()
