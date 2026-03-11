import uuid

from django.db import connection

from api.models import Category


class CategoryRepository:

    def find_by_company_id(self, company_id: uuid.UUID):
        return Category.objects.filter(company_id = company_id).order_by("created_at")

    def find(self, company_id: uuid.UUID, category_id: uuid.UUID):
        return Category.objects.filter(company_id=company_id, id = category_id).first()

    def get(self, company_id: uuid.UUID, category_id: uuid.UUID):
        return Category.objects.get(company_id=company_id, id=category_id)

    def create(self, company_id: uuid.UUID, name: str, parent_category_id: uuid.UUID|None):
        return Category.objects.create(
            company_id=company_id,
            name=name,
            parent_category_id=parent_category_id,
        )

    def update(self, category_id: uuid.UUID, name: str, parent_category_id: uuid.UUID|None):
        return Category.objects.filter(id=category_id).update(
            name=name,
            parent_category_id=parent_category_id,
        )

    def delete(self, category_id: uuid.UUID):
        return Category.objects.filter(id=category_id).delete()

    def has_children(self, category_id: uuid.UUID):
        return Category.objects.filter(parent_category_id=category_id).exists()

    def is_unique(self, company_id: uuid.UUID, name: str, except_id=None):
        query = Category.objects.filter(company_id=company_id, name=name)

        if except_id is not None:
            query = query.exclude(id=except_id)

        return not query.exists()


    def would_create_cycle(self, category_id: uuid.UUID, new_parent_category_id: uuid.UUID):
        """
        カテゴリの親を変更した際に循環参照になるかを確認する。
        
        :param category_id: 親を変更する対象のカテゴリID
        :param new_parent_category_id: 新しく設定しようとしている親カテゴリID
        :return: 循環参照になる場合は True、ならない場合は False
        """
        query = """
                WITH RECURSIVE ancestors AS (
                    SELECT id, parent_category_id
                    FROM categories
                    WHERE id = %s

                    UNION ALL

                    SELECT c.id, c.parent_category_id
                    FROM categories c
                             INNER JOIN ancestors a
                                        ON c.id = a.parent_category_id
                )
                SELECT 1
                FROM ancestors
                WHERE id = %s
                LIMIT 1
                """

        with connection.cursor() as cursor:
            cursor.execute(query, [new_parent_category_id, category_id])
            return cursor.fetchone() is not None
