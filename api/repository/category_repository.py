import uuid

from api.models import Category


class CategoryRepository:

    def find_by_company_id(self, company_id: uuid):
        return Category.objects.filter(company_id = company_id)

    def find(self, company_id: uuid, category_id: uuid):
        return Category.objects.filter(company_id = company_id, id = category_id).first()
