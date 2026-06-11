import uuid
from datetime import datetime, timezone
from unittest import TestCase

from api.domain.entities.category import Category
from api.domain.new_types.category_id import CategoryId
from api.domain.new_types.company_id import CompanyId


class TestCategoryEntity(TestCase):
    """Categoryエンティティの生成とフィールド保持を検証する。"""

    def test_create_category_without_parent(self):
        now = datetime.now(timezone.utc)
        company_id = CompanyId(uuid.uuid4())
        category_id = CategoryId(uuid.uuid4())

        category = Category(
            id=category_id,
            company_id=company_id,
            name="Backend",
            parent_category_id=None,
            created_at=now,
            updated_at=now,
        )

        self.assertEqual(category.id, category_id)
        self.assertEqual(category.company_id, company_id)
        self.assertEqual(category.name, "Backend")
        self.assertIsNone(category.parent_category_id)
        self.assertEqual(category.created_at, now)
        self.assertEqual(category.updated_at, now)

    def test_create_category_with_parent(self):
        now = datetime.now(timezone.utc)
        company_id = CompanyId(uuid.uuid4())
        category_id = CategoryId(uuid.uuid4())
        parent_id = CategoryId(uuid.uuid4())

        category = Category(
            id=category_id,
            company_id=company_id,
            name="Python",
            parent_category_id=parent_id,
            created_at=now,
            updated_at=now,
        )

        self.assertEqual(category.parent_category_id, parent_id)

    def test_category_is_immutable(self):
        """Categoryがfrozen=Trueで不変である。"""
        now = datetime.now(timezone.utc)
        company_id = CompanyId(uuid.uuid4())
        category_id = CategoryId(uuid.uuid4())

        category = Category(
            id=category_id,
            company_id=company_id,
            name="Backend",
            parent_category_id=None,
            created_at=now,
            updated_at=now,
        )

        with self.assertRaises(Exception):
            category.name = "Changed"  # type: ignore
