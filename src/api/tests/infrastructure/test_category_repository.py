from django.test import TestCase

from domain.entity.category import CategoryEntity
from domain.entity.company import CompanyEntity
from infrastructure.repository.category import CategoryRepository

class CategoryRepositoryTestCase(TestCase):

    def setUp(self):
        self.company_entity = CompanyEntity.new("Test Company")
        self.category_entity = CategoryEntity.new(self.company_entity, "Test Category", None)
        self.repository = CategoryRepository()

    def test_create_and_fetch(self):
        """
        カテゴリの作成と取得
        """
        created_category = self.repository.create(self.category_entity)

        fetched_category = self.repository.fetch(created_category.id)
        self.assertIsNotNone(fetched_category)
        self.assertEqual(fetched_category.name, "Test Category")

    def test_list_all(self):
        """
        カテゴリのリスト取得
        作成後にリスト取得して、作成したカテゴリの数が一致することを確認
        """
        self.repository.create(self.category_entity)
        self.repository.create(CategoryEntity.new(self.company_entity, "Another Category", None))

        categories = self.repository.list_all()
        self.assertEqual(len(categories), 2)

    def test_update(self):
        """
        カテゴリの更新
        作成後に更新して、値が更新されていることを確認
        """
        created_category = self.repository.create(self.category_entity)
        created_category.name = "Updated Category"

        self.repository.update(created_category)

        fetched_category = self.repository.fetch(created_category.id)
        self.assertEqual(fetched_category.name, "Updated Category")

    def test_delete(self):
        """
        カテゴリの削除
        作成後に削除して、取得できないことを確認
        """
        created_category = self.repository.create(self.category_entity)
        self.repository.delete(created_category.id)
        fetched_category = self.repository.fetch(created_category.id)
        self.assertIsNone(fetched_category)
