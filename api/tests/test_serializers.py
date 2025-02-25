import uuid
from django.test import TestCase

from api.serializers.category import CategorySerializer
from .factories import CategoryFactory, CompanyFactory


class TestCategorySerializer(TestCase):
    def test_company_if_not_given(self):
        serializer = CategorySerializer(data={})

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors.get('company')[0].code,
                         'required')

    def test_company_if_null(self):
        serializer = CategorySerializer(data={'company': None})

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors.get('company')[0].code,
                         'null')

    def test_company_if_blank(self):
        serializer = CategorySerializer(data={'company': ''})

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors.get('company')[0].code,
                         'null')

    def test_company_if_invalid(self):
        serializer = CategorySerializer(data={'company': 'invalid-id'})

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors.get('company')[0].code,
                         'invalid')

    def test_company_if_not_exist(self):
        serializer = CategorySerializer(data={'company': uuid.uuid4()})

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors.get('company')[0].code,
                         'does_not_exist')

    def test_company_if_it_has_subcategories(self):
        """サブカテゴリがある場合"""
        company = CompanyFactory()
        category = CategoryFactory()
        # サブカテゴリ
        CategoryFactory(
            company=category.company,
            parent_category=category,
        )

        serializer = CategorySerializer(
            instance=category,
            data={
                'company': company.id,
            },
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors.get('company')[0].code,
                         'has_subcategories')

    def test_name_if_not_given(self):
        serializer = CategorySerializer(data={})

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors.get('name')[0].code,
                         'required')

    def test_name_if_null(self):
        serializer = CategorySerializer(data={'name': None})

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors.get('name')[0].code,
                         'null')

    def test_name_if_blank(self):
        serializer = CategorySerializer(data={'name': ''})

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors.get('name')[0].code,
                         'blank')

    def test_name_if_too_long(self):
        serializer = CategorySerializer(data={'name': 'a' * 256})

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors.get('name')[0].code,
                         'max_length')

    def test_name_if_duplicated(self):
        """カテゴリ名重複 - 作成時"""
        other = CategoryFactory(
            name='category-name',
        )

        serializer = CategorySerializer(data={
            'company': other.company.id,
            'name': 'category-name',
        })

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors.get('name')[0].code,
                         'duplicated')

    def test_name_on_update_if_duplicated(self):
        """カテゴリ名重複 - 更新時"""
        category = CategoryFactory(
            name='category-name',
        )
        # 別のカテゴリ
        CategoryFactory(
            company=category.company,
            name='other-category-name',
        )

        serializer = CategorySerializer(
            instance=category,
            data={
                'name': 'other-category-name',
            },
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors.get('name')[0].code,
                         'duplicated')

    def test_name_on_company_update_if_duplicated(self):
        """カテゴリ名重複 - 企業更新時"""
        category_name = 'category-name'
        category = CategoryFactory(
            name=category_name,
        )
        other = CategoryFactory(
            name=category_name,
        )

        serializer = CategorySerializer(
            instance=category,
            data={
                'company': other.company.id,
            },
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors.get('name')[0].code,
                         'duplicated')

    def test_parent_category_if_not_exist(self):
        serializer = CategorySerializer(data={'parent_category': uuid.uuid4()})

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors.get('parent_category')[0].code,
                         'does_not_exist')

    def test_parent_category_if_invalid(self):
        """親カテゴリの企業IDと企業IDが一致しない場合 - 作成時"""
        company = CompanyFactory()
        category = CategoryFactory()

        serializer = CategorySerializer(data={
            'company': company.id,
            'name': 'category-name',
            'parent_category': category.id,
        })

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors.get('parent_category')[0].code,
                         'invalid')

    def test_parent_category_on_update_if_invalid(self):
        """親カテゴリの企業IDと企業IDが一致しない場合 - 更新時"""
        parent_category = CategoryFactory()
        other_parent_category = CategoryFactory()
        category = CategoryFactory(
            company=parent_category.company,
            parent_category=parent_category,
        )

        serializer = CategorySerializer(
            instance=category,
            data={
                'parent_category': other_parent_category.id,
            },
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors.get('parent_category')[0].code,
                         'invalid')

    def test_parent_category_on_company_update_if_invalid(self):
        """親カテゴリの企業IDと企業IDが一致しない場合 - 企業更新時"""
        company = CompanyFactory()
        parent_category = CategoryFactory()
        category = CategoryFactory(
            company=parent_category.company,
            parent_category=parent_category,
        )

        serializer = CategorySerializer(
            instance=category,
            data={
                'company': company.id,
            },
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors.get('parent_category')[0].code,
                         'invalid')
