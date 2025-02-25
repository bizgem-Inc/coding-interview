from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Category
from .factories import CategoryFactory, CompanyFactory


class CategoryViewTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.TARGET_URL = '/api/categories/'

        cls.company = CompanyFactory()

        cls.parent_category = CategoryFactory(
            company=cls.company,
            name='parent-category-name',
        )
        cls.sub_category = CategoryFactory(
            company=cls.company,
            name='sub-category-name',
            parent_category=cls.parent_category,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_list(self):
        response = self.client.get(self.TARGET_URL)
        expected = [
            {
                'id': self.parent_category.id,
                'company': self.company.id,
                'name': 'parent-category-name',
                'parent_category': None,
            },
            {
                'id': self.sub_category.id,
                'company': self.company.id,
                'name': 'sub-category-name',
                'parent_category': self.parent_category.id,
            },
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.json(), expected)

    def test_retrieve_for_parent_category(self):
        response = self.client.get(
            f'{self.TARGET_URL}{self.parent_category.id}/',
        )
        expected = {
            'id': self.parent_category.id,
            'company': self.company.id,
            'name': 'parent-category-name',
            'parent_category': None,
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(response.content, expected)

    def test_retrieve_for_sub_category(self):
        response = self.client.get(
            f'{self.TARGET_URL}{self.sub_category.id}/',
        )
        expected = {
            'id': self.sub_category.id,
            'company': self.company.id,
            'name': 'sub-category-name',
            'parent_category': self.parent_category.id,
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(response.content, expected)

    def test_retrieve_for_non_existence(self):
        response = self.client.get(
            f'{self.TARGET_URL}non-existence-id/',
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_success_for_parent_category(self):
        category_name = 'new-category-name'
        params = {
            'company': self.company.id,
            'name': category_name,
        }
        category_count = Category.objects.count()

        response = self.client.post(
            self.TARGET_URL,
            params,
            format='json',
        )

        created = Category.objects.get(name=category_name)
        expected = {
            'id': str(created.id),
            'company': self.company.id,
            'name': category_name,
            'parent_category': None,
        }

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), category_count + 1)
        self.assertJSONEqual(response.content, expected)

    def test_create_success_for_sub_category(self):
        category_name = 'new-category-name'
        params = {
            'company': self.company.id,
            'name': category_name,
            'parent_category': self.parent_category.id,
        }
        category_count = Category.objects.count()

        response = self.client.post(
            self.TARGET_URL,
            params,
            format='json',
        )

        created = Category.objects.get(name=category_name)
        expected = {
            'id': str(created.id),
            'company': self.company.id,
            'name': category_name,
            'parent_category': self.parent_category.id,
        }

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), category_count + 1)
        self.assertJSONEqual(response.content, expected)

    def test_create_invalid_request(self):
        params = {
            'company': self.company.id,
            'name': 'a' * 256,
        }
        category_count = Category.objects.count()

        response = self.client.post(
            self.TARGET_URL,
            params,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Category.objects.count(), category_count)

    def test_update_company(self):
        category = CategoryFactory()
        params = {
            'company': self.company.id,
        }
        expected = {
            'id': str(category.id),
            'company': self.company.id,
            'name': category.name,
            'parent_category': None,
        }

        response = self.client.patch(
            f'{self.TARGET_URL}{category.id}/',
            params,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(response.content, expected)

    def test_update_name(self):
        category_name = 'category-name-updated'
        category = CategoryFactory()
        params = {
            'name': category_name,
        }
        expected = {
            'id': str(category.id),
            'company': category.company.id,
            'name': category_name,
            'parent_category': None,
        }

        response = self.client.patch(
            f'{self.TARGET_URL}{category.id}/',
            params,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(response.content, expected)

    def test_update_parent_category(self):
        parent_category = CategoryFactory()
        other_parent_category = CategoryFactory(
            company=parent_category.company,
        )
        category = CategoryFactory(
            company=parent_category.company,
            parent_category=parent_category,
        )
        params = {
            'parent_category': other_parent_category.id,
        }
        expected = {
            'id': str(category.id),
            'company': category.company.id,
            'name': category.name,
            'parent_category': other_parent_category.id,
        }

        response = self.client.patch(
            f'{self.TARGET_URL}{category.id}/',
            params,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(response.content, expected)

    def test_update_parent_category_to_null(self):
        parent_category = CategoryFactory()
        category = CategoryFactory(
            company=parent_category.company,
            parent_category=parent_category,
        )
        params = {
            'parent_category': None,
        }
        expected = {
            'id': str(category.id),
            'company': category.company.id,
            'name': category.name,
            'parent_category': None,
        }

        response = self.client.patch(
            f'{self.TARGET_URL}{category.id}/',
            params,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(response.content, expected)

    def test_update_all(self):
        category_name = 'category-name-updated'
        parent_category = CategoryFactory()
        other_parent_category = CategoryFactory()
        category = CategoryFactory(
            company=parent_category.company,
            parent_category=parent_category,
        )
        params = {
            'company': other_parent_category.company.id,
            'name': category_name,
            'parent_category': other_parent_category.id,
        }
        expected = {
            'id': str(category.id),
            'company': other_parent_category.company.id,
            'name': category_name,
            'parent_category': other_parent_category.id,
        }

        response = self.client.put(
            f'{self.TARGET_URL}{category.id}/',
            params,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(response.content, expected)

    def test_destroy(self):
        category = CategoryFactory()
        sub_category = CategoryFactory(
            company=category.company,
            parent_category=category,
        )

        response = self.client.delete(
            f'{self.TARGET_URL}{category.id}/',
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        sub_category_updated = Category.objects.get(pk=sub_category.id)
        self.assertEqual(Category.objects.filter(pk=category.id).count(), 0)
        self.assertIsNone(sub_category_updated.parent_category)
