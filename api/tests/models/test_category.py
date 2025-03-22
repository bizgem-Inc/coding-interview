import math
import time

from django.test import TestCase
from django.db.utils import DataError, IntegrityError

from api.models.company import Company
from api.models.category import Category

class CategoryModelCompanyTest(TestCase):
    def test_related_name_is_plus(self):
        company = Company.objects.create(name="会社１")
        category = Category.objects.create(name="カテゴリ１", company=company)

        company.refresh_from_db()

        with self.assertRaises(AttributeError):
            company.category_set

    def test_on_delete_is_CASCADE(self):
        company = Company.objects.create(name="会社１")
        Category.objects.create(name="カテゴリ１", company=company)

        company.delete()

        self.assertFalse(Category.objects.all().exists())

class CategoryModelNameTest(TestCase):
    def test_max_length_is_255(self):
        company = Company.objects.create(name="会社１")

        valid_name_category = Category.objects.create(name="あ"*255, company=company)
        # DoesNotExist例外が発生していないことで間接的に確認
        self.assertTrue(Category.objects.get(id=valid_name_category.id))

        with self.assertRaises(DataError):
            valid_name_category = Category.objects.create(name="あ"*256, company=company)

class CategoryModelParentCategoryTest(TestCase):
    def test_related_name_is_plus(self):
        company = Company.objects.create(name="会社１")
        parent_category = Category.objects.create(name="カテゴリ１", company=company)
        category = Category.objects.create(
            name="カテゴリ２",
            company=company,
            parent_category=parent_category
        )

        parent_category.refresh_from_db()

        with self.assertRaises(AttributeError):
            parent_category.category_set

    def test_on_delete_is_SET_NULL(self):
        company = Company.objects.create(name="会社１")
        grand_parent_category = Category.objects.create(name="カテゴリ３", company=company)
        parent_category = Category.objects.create(
            name="カテゴリ１",
            company=company,
            parent_category=grand_parent_category,
        )
        category = Category.objects.create(
            name="カテゴリ２",
            company=company,
            parent_category=parent_category
        )

        parent_category.delete()
        category.refresh_from_db()

        self.assertIsNone(category.parent_category)

        grand_parent_category.refresh_from_db()
        self.assertTrue(grand_parent_category.id)

class CategoryModelCreatedAtTest(TestCase):
    def test_auto_now_add_is_True(self):
        company = Company.objects.create(name="会社１")
        category = Category.objects.create(name="カテゴリ１", company=company)

        self.assertIsNotNone(category.created_at)

class CategoryModelUpdatedAtTest(TestCase):
    def test_field_auto_now_is_True(self):
        company = Company.objects.create(name="会社１")
        category = Category.objects.create(name="カテゴリ１", company=company)

        self.assertIsNotNone(category.updated_at)

        # 新規作成時でも、ミリ秒単位ではずれてしまうので秒単位で比較
        self.assertEqual(
            math.floor(category.updated_at.timestamp()),
            math.floor(category.created_at.timestamp()),
        )

        category.name = "カテゴリ２"
        time.sleep(1)
        category.save()

        category.refresh_from_db()

        self.assertGreater(
            math.floor(category.updated_at.timestamp()),
            math.floor(category.created_at.timestamp()),
        )

class CategoryModelMetaConstraintsTest(TestCase):
    def test_unique_constraints_with_company_and_name(self):
        company = Company.objects.create(name="会社１")
        category = Category.objects.create(name="カテゴリ１", company=company)

        with self.assertRaises(IntegrityError):
            category = Category.objects.create(name="カテゴリ１", company=company)