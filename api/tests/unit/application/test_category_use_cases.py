import uuid
from datetime import datetime, timezone
from typing import Optional
from unittest import TestCase

from api.application.dto.category import (
    CategoryResponse,
    CreateCategoryRequest,
    UpdateCategoryRequest,
)
from api.application.ports.category_repository import CategoryRepository
from api.application.use_cases.category.create import CreateCategory
from api.application.use_cases.category.delete import DeleteCategory
from api.application.use_cases.category.get import GetCategory
from api.application.use_cases.category.list import ListCategories
from api.application.use_cases.category.update import UpdateCategory
from api.domain.entities.category import Category
from api.domain.exceptions import (
    CategoryNotFoundError,
    DuplicateCategoryNameError,
    ReferencedCategoryNotFoundError,
)
from api.domain.new_types.category_id import CategoryId
from api.domain.new_types.company_id import CompanyId


class InMemoryCategoryRepository:
    """Use Caseテスト用のインメモリRepository。"""

    def __init__(self) -> None:
        self._store: dict[CategoryId, Category] = {}

    def find_by_id(self, category_id: CategoryId) -> Optional[Category]:
        return self._store.get(category_id)

    def find_all(self, limit: int = 10, offset: int = 0) -> list[Category]:
        items = list(self._store.values())
        return items[offset : offset + limit]

    def save(self, category: Category) -> Category:
        self._store[category.id] = category
        return category

    def delete(self, category_id: CategoryId) -> None:
        self._store.pop(category_id, None)

    def find_by_company_and_name(
        self, company_id: CompanyId, name: str
    ) -> Optional[Category]:
        for c in self._store.values():
            if c.company_id == company_id and c.name == name:
                return c
        return None

    def find_parent_by_id(
        self, parent_category_id: CategoryId
    ) -> Optional[Category]:
        return self._store.get(parent_category_id)

    def company_exists(self, company_id: CompanyId) -> bool:
        # インメモリではcompany_idの追跡を行わない（Use Caseテストの範囲外）
        return True


def _make_category(
    category_id: Optional[CategoryId] = None,
    company_id: Optional[CompanyId] = None,
    name: str = "Test",
    parent_id: Optional[CategoryId] = None,
) -> Category:
    now = datetime.now(timezone.utc)
    return Category(
        id=category_id or CategoryId(uuid.uuid4()),
        company_id=company_id or CompanyId(uuid.uuid4()),
        name=name,
        parent_category_id=parent_id,
        created_at=now,
        updated_at=now,
    )


class TestListCategories(TestCase):
    def test_returns_empty_list(self):
        repo = InMemoryCategoryRepository()
        use_case = ListCategories(repo)
        result = use_case.execute()
        self.assertEqual(result, [])

    def test_returns_all_categories(self):
        repo = InMemoryCategoryRepository()
        cat = _make_category(name="Backend")
        repo.save(cat)
        use_case = ListCategories(repo)
        result = use_case.execute()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "Backend")

    def test_returns_paginated_categories(self):
        repo = InMemoryCategoryRepository()
        for name in ("A", "B", "C", "D", "E"):
            repo.save(_make_category(name=name))
        use_case = ListCategories(repo)
        result = use_case.execute(limit=2, offset=0)
        self.assertEqual(len(result), 2)
        result = use_case.execute(limit=2, offset=2)
        self.assertEqual(len(result), 2)
        result = use_case.execute(limit=2, offset=4)
        self.assertEqual(len(result), 1)


class TestGetCategory(TestCase):
    def test_returns_category(self):
        repo = InMemoryCategoryRepository()
        cat = _make_category(name="Backend")
        repo.save(cat)
        use_case = GetCategory(repo)
        result = use_case.execute(cat.id)
        self.assertIsInstance(result, CategoryResponse)
        self.assertEqual(result.name, "Backend")

    def test_raises_when_not_found(self):
        repo = InMemoryCategoryRepository()
        use_case = GetCategory(repo)
        with self.assertRaises(CategoryNotFoundError):
            use_case.execute(CategoryId(uuid.uuid4()))


class TestCreateCategory(TestCase):
    def test_creates_category(self):
        repo = InMemoryCategoryRepository()
        company_id = CompanyId(uuid.uuid4())
        request = CreateCategoryRequest(
            company_id=company_id,
            name="Backend",
            parent_category_id=None,
        )
        use_case = CreateCategory(repo)
        result = use_case.execute(request)
        self.assertEqual(result.name, "Backend")
        self.assertEqual(result.company_id, company_id)
        self.assertIsNone(result.parent_category_id)

    def test_raises_on_duplicate_name(self):
        repo = InMemoryCategoryRepository()
        company_id = CompanyId(uuid.uuid4())
        existing = _make_category(company_id=company_id, name="Backend")
        repo.save(existing)
        request = CreateCategoryRequest(
            company_id=company_id,
            name="Backend",
            parent_category_id=None,
        )
        use_case = CreateCategory(repo)
        with self.assertRaises(DuplicateCategoryNameError):
            use_case.execute(request)

    def test_raises_on_missing_parent(self):
        repo = InMemoryCategoryRepository()
        request = CreateCategoryRequest(
            company_id=CompanyId(uuid.uuid4()),
            name="Backend",
            parent_category_id=CategoryId(uuid.uuid4()),
        )
        use_case = CreateCategory(repo)
        with self.assertRaises(ReferencedCategoryNotFoundError):
            use_case.execute(request)


class TestUpdateCategory(TestCase):
    def test_updates_category(self):
        repo = InMemoryCategoryRepository()
        cat = _make_category(name="Old")
        repo.save(cat)
        request = UpdateCategoryRequest(
            company_id=cat.company_id,
            name="New",
            parent_category_id=None,
        )
        use_case = UpdateCategory(repo)
        result = use_case.execute(cat.id, request)
        self.assertEqual(result.name, "New")

    def test_raises_when_not_found(self):
        repo = InMemoryCategoryRepository()
        request = UpdateCategoryRequest(
            company_id=CompanyId(uuid.uuid4()),
            name="New",
            parent_category_id=None,
        )
        use_case = UpdateCategory(repo)
        with self.assertRaises(CategoryNotFoundError):
            use_case.execute(CategoryId(uuid.uuid4()), request)


class TestDeleteCategory(TestCase):
    def test_deletes_category(self):
        repo = InMemoryCategoryRepository()
        cat = _make_category()
        repo.save(cat)
        use_case = DeleteCategory(repo)
        use_case.execute(cat.id)
        self.assertIsNone(repo.find_by_id(cat.id))

    def test_raises_when_not_found(self):
        repo = InMemoryCategoryRepository()
        use_case = DeleteCategory(repo)
        with self.assertRaises(CategoryNotFoundError):
            use_case.execute(CategoryId(uuid.uuid4()))
