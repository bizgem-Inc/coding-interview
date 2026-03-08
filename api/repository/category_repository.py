import uuid

from api.models import Category


class CategoryRepository:

    def find_by_company_id(self, company_id: uuid.UUID):
        return Category.objects.filter(company_id = company_id)

    def find(self, company_id: uuid.UUID, category_id: uuid.UUID):
        return Category.objects.filter(company_id=company_id, id = category_id).first()

    def create(self, company_id: uuid.UUID, name: str, parent_category_id: uuid.UUID|None):
        return Category.objects.create(
            company_id=company_id,
            name=name,
            parent_category_id=parent_category_id,
        )

    def delete(self, category_id: uuid.UUID):
        return Category.objects.filter(id=category_id).delete()

    def has_children(self, category_id: uuid.UUID):
        return Category.objects.filter(parent_category_id=category_id).exists()

    def is_unique(self, company_id: uuid.UUID, name: str):
        return not Category.objects.filter(company_id=company_id, name=name).exists()

