from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from api.models import Company, Category


class CategoryModelTest(TestCase):
    def test_clean_prevent_self_parent(self):
        company = Company.objects.create(name="テスト企業１")
        category = Category.objects.create(name="テストカテゴリー１", company=company)
        category.parent_category = category

        with self.assertRaises(ValidationError):
            category.clean()

    def test_db_constraints_prevent_self_parent(self):
        company = Company.objects.create(name="テスト企業１")
        category = Category.objects.create(name="テストカテゴリー１", company=company)
        category.parent_category = category
        with self.assertRaises(IntegrityError):
            category.save()
