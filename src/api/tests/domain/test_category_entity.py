from django.test import TestCase

from uuid import uuid4, UUID
from datetime import datetime
from domain.entity.company import CompanyEntity
from domain.entity.category import CategoryEntity


class TestCategoryEntity(TestCase):

    def setUp(self):
        self.company = CompanyEntity(
            id=uuid4(),
            name="Test Company",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.parent_category = CategoryEntity(
            id=uuid4(),
            company=self.company,
            name="Test Parent Category",
            parent_category=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    def test_new_entity(self):
        """
        初めてエンティティが生成される際にアプリケーション側ではidやcreated_at, updated_atを設定しない
        入れた値については正しいことを確認
        """
        category = CategoryEntity.new(self.company, "Test Category", self.parent_category)
        self.assertIsNone(category.id)
        self.assertIsNone(category.created_at)
        self.assertIsNone(category.updated_at)

        self.assertEqual(category.company, self.company)
        self.assertEqual(category.name, "Test Category")
        self.assertEqual(category.parent_category, self.parent_category)

    def test_from_record(self):
        """
        永続化された既存データからエンティティを生成する際にはidやcreated_at, updated_atを設定される
        入れた値は正しいことを確認
        """
        category = CategoryEntity.from_record(
            uuid4(), self.company, "Test Category", self.parent_category, datetime.now(), datetime.now()
        )
        self.assertIsNotNone(category.id)
        self.assertIsNotNone(category.created_at)
        self.assertIsNotNone(category.updated_at)

        self.assertEqual(category.company, self.company)
        self.assertEqual(category.name, "Test Category")
        self.assertEqual(category.parent_category, self.parent_category)

    def test_validate_name(self):
        """
        名前のバリデーションのしきい値テスト、not validパターン
        """
        with self.assertRaises(ValueError):
            CategoryEntity.new(self.company, "a" * 256, self.parent_category)

    def test_validate_name_ok(self):
        """
        名前のバリデーションのしきい値テスト、validパターン
        """
        CategoryEntity.new(self.company, "a" * 255, self.parent_category)

    def test_change_name(self):
        """
        名前が変更されることを確認
        """
        category = CategoryEntity.new(self.company, "Test Category", self.parent_category)
        category.change_name("New Category")
        self.assertEqual(category.name, "New Category")

    def test_change_parent_category(self):
        """
        親カテゴリーが変更されることを確認
        """
        new_parent = CategoryEntity.new(self.company, "New Parent", None)
        category = CategoryEntity.new(self.company, "Test Category", self.parent_category)
        category.change_parent_category(new_parent)
        self.assertEqual(category.parent_category, new_parent)

    def test_change_company(self):
        """
        会社が変更されることを確認
        """
        new_company = CompanyEntity(
            id=uuid4(),
            name="New Company",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        category = CategoryEntity.new(self.company, "Test Category", self.parent_category)
        category.change_company(new_company)
        self.assertEqual(category.company, new_company)

    def test_to_dict(self):
        """
        to_dictメソッドが正しく動作するか確認
        """
        category = CategoryEntity.from_record(
            uuid4(), self.company, "Test Category", self.parent_category, datetime.now(), datetime.now()
        )
        result = category.to_dict()

        self.assertEqual(result["id"], str(category.id))
        self.assertEqual(result["company"], category.company.to_dict())
        self.assertEqual(result["name"], category.name)
        self.assertEqual(result["parent_category"], category.parent_category.to_dict())
        self.assertEqual(result["created_at"], category.created_at.isoformat())
        self.assertEqual(result["updated_at"], category.updated_at.isoformat())
