import uuid
from datetime import datetime, timezone
from unittest import TestCase

from django.test import TransactionTestCase

from api.domain.entities.category import Category
from api.domain.new_types.category_id import CategoryId
from api.domain.new_types.company_id import CompanyId
from api.repositories.django.category import DjangoCategoryRepository
from api.repositories.django.mappers.category import to_domain, to_model
from api.repositories.django.orm_models.category import CategoryModel
from api.repositories.django.orm_models.company import CompanyModel


class CategoryRepositoryTests(TransactionTestCase):
    """Django CategoryRepositoryとMapperの結合テスト。"""

    available_apps = ["api"]

    def setUp(self):
        self.repository = DjangoCategoryRepository()
        self.company = CompanyModel.objects.create(name="TestCorp")

    def _make_domain_category(
        self,
        company=None,
        name="Test",
        parent_id=None,
        category_id=None,
    ) -> Category:
        now = datetime.now(timezone.utc)
        return Category(
            id=category_id or CategoryId(uuid.uuid4()),
            company_id=CompanyId((company or self.company).id),
            name=name,
            parent_category_id=parent_id,
            created_at=now,
            updated_at=now,
        )

    def test_save_and_find_by_id(self):
        cat = self._make_domain_category(name="Backend")
        saved = self.repository.save(cat)
        found = self.repository.find_by_id(saved.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Backend")  # type: ignore[union-attr]

    def test_find_by_id_returns_none_for_missing(self):
        found = self.repository.find_by_id(CategoryId(uuid.uuid4()))
        self.assertIsNone(found)

    def test_find_all(self):
        cat1 = self._make_domain_category(name="Backend")
        cat2 = self._make_domain_category(name="Frontend")
        self.repository.save(cat1)
        self.repository.save(cat2)
        all_cats = self.repository.find_all()
        self.assertEqual(len(all_cats), 2)

    def test_save_updates_existing(self):
        cat = self._make_domain_category(name="Old")
        self.repository.save(cat)
        now = datetime.now(timezone.utc)
        updated = Category(
            id=cat.id,
            company_id=cat.company_id,
            name="New",
            parent_category_id=None,
            created_at=cat.created_at,
            updated_at=now,
        )
        self.repository.save(updated)
        found = self.repository.find_by_id(cat.id)
        self.assertEqual(found.name, "New")  # type: ignore[union-attr]

    def test_delete(self):
        cat = self._make_domain_category(name="Backend")
        self.repository.save(cat)
        self.repository.delete(cat.id)
        found = self.repository.find_by_id(cat.id)
        self.assertIsNone(found)

    def test_find_by_company_and_name(self):
        cat = self._make_domain_category(name="Backend")
        self.repository.save(cat)
        found = self.repository.find_by_company_and_name(
            CompanyId(self.company.id), "Backend"
        )
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Backend")  # type: ignore[union-attr]

    def test_find_by_company_and_name_returns_none_when_missing(self):
        found = self.repository.find_by_company_and_name(
            CompanyId(self.company.id), "Missing"
        )
        self.assertIsNone(found)

    def test_duplicate_constraint_raises(self):
        """同一Company内で重複名が保存できない。"""
        cat1 = self._make_domain_category(name="Backend")
        cat2 = self._make_domain_category(name="Backend")
        self.repository.save(cat1)
        with self.assertRaises(Exception):
            self.repository.save(cat2)

    def test_mapper_roundtrip(self):
        """Mapperの往復変換が整合する。"""
        from api.repositories.django.mappers.category import to_model

        cat = self._make_domain_category(name="Backend")
        model = to_model(cat, self.company)
        self.assertEqual(model.name, "Backend")
        self.assertEqual(model.company.id, self.company.id)
        domain_back = to_domain(model)
        self.assertEqual(domain_back.id, cat.id)
        self.assertEqual(domain_back.name, cat.name)

    def test_find_parent_by_id(self):
        parent = self._make_domain_category(name="Parent")
        self.repository.save(parent)
        found = self.repository.find_parent_by_id(parent.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.id, parent.id)  # type: ignore[union-attr]

    def test_find_parent_by_id_returns_none_for_missing(self):
        found = self.repository.find_parent_by_id(CategoryId(uuid.uuid4()))
        self.assertIsNone(found)
