from django.test import TestCase

from api.models.category import Category
from api.models.company import Company
from api.repositories.category_repository import CategoryRepository


class TestCategoryRepository(TestCase):
    def setUp(self):
        self.repository = CategoryRepository()

        self.company = Company.objects.create(name="テスト会社")
        self.parent_category = Category.objects.create(
            company_id=self.company.id, name="親カテゴリ"
        )
        self.category = Category.objects.create(
            company_id=self.company.id,
            name="テストカテゴリ",
            parent_category_id=self.parent_category.id,
        )

        self.other_company = Company.objects.create(name="他社")
        self.other_company_category = Category.objects.create(
            company_id=self.other_company.id, name="他社カテゴリ"
        )

    def test_get_categories(self):
        categories = self.repository.get_categories(self.company.id)

        self.assertEqual(categories.count(), 2)
        self.assertIn(self.parent_category, categories)
        self.assertIn(self.category, categories)

        other_categories = self.repository.get_categories(self.other_company.id)
        self.assertEqual(other_categories.count(), 1)
        self.assertIn(self.other_company_category, other_categories)

    def test_get_category_by_id(self):
        retrieved_category = self.repository.get_category_by_id(self.category.id)
        self.assertEqual(retrieved_category.id, self.category.id)
        self.assertEqual(retrieved_category.name, "テストカテゴリ")
        self.assertEqual(retrieved_category.parent_category.id, self.parent_category.id)

    def test_create_category(self):
        # 親カテゴリなしで作成
        new_category = self.repository.create_category(
            company_id=self.company.id, name="新規カテゴリ"
        )

        self.assertIsNotNone(new_category.id)
        self.assertEqual(new_category.name, "新規カテゴリ")
        self.assertEqual(new_category.company.id, self.company.id)
        self.assertIsNone(new_category.parent_category)

        # 親カテゴリありで作成
        new_child_category = self.repository.create_category(
            company_id=self.company.id,
            name="子カテゴリ",
            parent_category_id=self.parent_category.id,
        )

        self.assertEqual(new_child_category.name, "子カテゴリ")
        self.assertEqual(new_child_category.parent_category.id, self.parent_category.id)

    def test_update_category(self):
        # 名前を更新
        self.repository.update_category(
            category_id=self.category.id, name="更新後カテゴリ"
        )

        category = Category.objects.get(id=self.category.id)
        self.assertEqual(category.name, "更新後カテゴリ")
        self.assertEqual(category.parent_category.id, self.parent_category.id)

        # 親カテゴリを更新（親なしに変更）
        self.repository.update_category(
            category_id=self.category.id, name="更新後カテゴリ", parent_category_id=None
        )

        category = Category.objects.get(id=self.category.id)
        self.assertIsNone(category.parent_category)

    def test_delete_category(self):
        category_id = self.category.id
        self.repository.delete_category(category_id)

        with self.assertRaises(Category.DoesNotExist):
            Category.objects.get(id=category_id)
