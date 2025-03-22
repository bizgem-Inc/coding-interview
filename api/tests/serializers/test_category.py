import uuid

from django.test import TestCase
from django.db.utils import DataError

from api.models.category import Category
from api.models.company import Company
from api.serializers.category import CategorySerializer

class CategorySerializerValidationCompanyTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="会社１")

    def test_create_validation(self):
        # 存在するCompanyのidを指定する場合
        serializer = CategorySerializer(data={
            "company": self.company.id,
            "name": "カテゴリ１"
        })
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.errors, {})
        category = serializer.save()
        self.assertTrue(category.id)

        # 存在しないCompanyのidを指定する場合
        serializer = CategorySerializer(data={
            "company": uuid.uuid4(),
            "name": "カテゴリ２"
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn("company", serializer.errors.keys())

        # Companyのidを指定しない場合
        serializer = CategorySerializer(data={
            "name": "カテゴリ２"
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn("company", serializer.errors.keys())

    def test_update_validation(self):
        another_company = Company.objects.create(name="会社２")
        category = Category.objects.create(name="カテゴリ１", company=self.company)

        # 有効な別のCompanyのidを指定する場合
        serializer = CategorySerializer(category, data={
            "company": another_company.id
        }, partial=True)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.errors, {})
        saved_category = serializer.save()
        self.assertEqual(saved_category.company, another_company)

        # 存在しないCompanyのidを指定する場合
        serializer = CategorySerializer(category, data={
            "company": uuid.uuid4(),
        }, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn("company", serializer.errors.keys())

        # Companyのidを指定しない場合
        serializer = CategorySerializer(category, data={
            "company": None
        }, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn("company", serializer.errors.keys())

class CategorySerializerValidationNameTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="会社１")

    def test_create_validation(self):
        # 有効な文字数の場合    　
        serializer = CategorySerializer(data={
            "company": self.company.id,
            "name": "あ" * 255,
        })
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.errors, {})
        category = serializer.save()
        self.assertTrue(category.id)

        # 空白の場合
        serializer = CategorySerializer(data={
            "company": self.company.id,
            "name": "",
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors.keys())

        # 文字数超過の場合
        serializer = CategorySerializer(data={
            "company": self.company.id,
            "name": "あ" * 256,
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors.keys())

    def test_update_validation(self):
        category = Category.objects.create(name="カテゴリ１", company=self.company)

        # 有効な文字数の場合　
        serializer = CategorySerializer(category, data={"name": "あ" * 255}, partial=True)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.errors, {})
        saved_category = serializer.save()
        saved_category.refresh_from_db()
        self.assertEqual(saved_category.name, "あ" * 255)

        # 空白の場合
        serializer = CategorySerializer(category, data={"name": ""}, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors.keys())

        # 文字数超過の場合
        serializer = CategorySerializer(category, data={"name": "あ" * 256}, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors.keys())

class CategorySerializerValidationParentCategoryTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="会社１")
        self.category = Category.objects.create(name="カテゴリ１", company=self.company)
        self.another_category = Category.objects.create(name="カテゴリ２", company=self.company)

    def test_create_validation(self):
        # 有効なcategoryのidを指定した場合
        serializer = CategorySerializer(data={
            "company": self.company.id,
            "name": "カテゴリ３",
            "parent_category": self.category.id
        })
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.errors, {})
        category = serializer.save()
        self.assertTrue(category.id)

        # 指定しない場合
        serializer = CategorySerializer(data={
            "company": self.company.id,
            "name": "カテゴリ４",
            "parent_category": None,
        })
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.errors, {})
        category = serializer.save()
        self.assertTrue(category.id)

        # 無効なcategoryのidを指定した場合
        serializer = CategorySerializer(data={
            "company": self.company.id,
            "name": "カテゴリ５",
            "parent_category": uuid.uuid4(),
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn("parent_category", serializer.errors.keys())

    def test_update_validation(self):
        category = Category.objects.create(
            company=self.company,
            name="カテゴリ３",
            parent_category=self.category
        )

        # 有効なCategoryのidを指定した場合
        serializer = CategorySerializer(
            category,
            data={"parent_category": self.another_category.id},
            partial=True
        )
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.errors, {})
        saved_category = serializer.save()
        saved_category.refresh_from_db()
        self.assertEqual(saved_category.parent_category, self.another_category)

        # 指定しない場合
        serializer = CategorySerializer(
            category,
            data={"parent_category": None},
            partial=True
        )
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.errors, {})
        saved_category = serializer.save()
        saved_category.refresh_from_db()
        self.assertIsNone(saved_category.parent_category)

        # 無効なidを指定した場合
        serializer = CategorySerializer(
            category,
            data={"parent_category": uuid.uuid4()},
            partial=True
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("parent_category", serializer.errors.keys())

        # 自身のidを指定した場合
        serializer = CategorySerializer(
            category,
            data={"parent_category": category.id},
            partial=True
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("parent_category", serializer.errors.keys())

class CategorySerializerValidationCompanyCategoryCombinationTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="会社１")
        self.category = Category.objects.create(name="カテゴリ１", company=self.company)

    def test_create_validation(self):
        serializer = CategorySerializer(data={
            "company": self.company.id,
            "name": "カテゴリ１"
        })
        self.assertFalse(serializer.is_valid())

    def test_update_validation(self):
        another_company = Company.objects.create(name="会社２")
        another_category = Category.objects.create(name="カテゴリ１", company=another_company)

        serializer = CategorySerializer(self.category, data={
            "company": another_company.id
        }, partial=True)
        self.assertFalse(serializer.is_valid())