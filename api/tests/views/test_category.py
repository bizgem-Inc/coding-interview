from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.forms.models import model_to_dict

from api.models.company import Company
from api.models.category import Category

class CategoryViewListTest(APITestCase):
    def setUp(self):
        self.url = reverse("category-list")

    def test_category_is_not_existed(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_categories_are_existed(self):
        company = Company.objects.create(name="会社１")
        category_1 = Category.objects.create(name="カテゴリ１", company=company)
        category_2 = Category.objects.create(
            name="カテゴリ２",
            company=company,
            parent_category=category_1,
        )
        category_3 = Category.objects.create(name="カテゴリ３", company=company)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        items_by_id = {item["id"]: item for item in response.data}

        self.assertEqual(
            items_by_id[str(category_1.id)],
            {
                "id": str(category_1.id),
                "name": "カテゴリ１",
                "company": company.id,
                "parent_category": None,
                "created_at": category_1.created_at.isoformat().replace("+00:00", "Z"),
                "updated_at": category_1.updated_at.isoformat().replace("+00:00", "Z"),
            }
        )
        self.assertEqual(
            items_by_id[str(category_2.id)],
            {
                "id": str(category_2.id),
                "name": "カテゴリ２",
                "company": company.id,
                "parent_category": category_1.id,
                "created_at": category_2.created_at.isoformat().replace("+00:00", "Z"),
                "updated_at": category_2.updated_at.isoformat().replace("+00:00", "Z"),
            }
        )
        self.assertEqual(
            items_by_id[str(category_3.id)],
            {
                "id": str(category_3.id),
                "name": "カテゴリ３",
                "company": company.id,
                "parent_category": None,
                "created_at": category_3.created_at.isoformat().replace("+00:00", "Z"),
                "updated_at": category_3.updated_at.isoformat().replace("+00:00", "Z"),
            }
        )

class CategoryViewDetailTest(APITestCase):
    def test_category_is_not_existed(self):
        response = self.client.get(reverse("category-detail", args=[1]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_category_is_existed(self):
        company = Company.objects.create(name="会社１")
        category_1 = Category.objects.create(name="カテゴリ１", company=company)
        category_2 = Category.objects.create(
            name="カテゴリ２",
            company=company,
            parent_category=category_1,
        )

        response = self.client.get(reverse("category-detail", args=[str(category_2.id)]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "id": str(category_2.id),
                "name": "カテゴリ２",
                "company": company.id,
                "parent_category": category_1.id,
                "created_at": category_2.created_at.isoformat().replace("+00:00", "Z"),
                "updated_at": category_2.updated_at.isoformat().replace("+00:00", "Z"),
            }
        )

class CategoryViewCreateTest(APITestCase):
    def setUp(self):
        self.url = reverse("category-list")
        self.company = Company.objects.create(name="会社１")

    def test_invalid_data(self):
        data = {
            "company": self.company.id,
            "name": "あ" * 256,
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_data(self):
        parent_category = Category.objects.create(name="カテゴリ１", company=self.company)
        data = {
            "company": self.company.id,
            "name": "あ" * 255,
            "parent_category": parent_category.id
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(
            Category.objects.filter(
                company=self.company.id,
                name="あ" * 255,
                parent_category=parent_category.id
            ).exists()
        )

class CategoryViewUpdateTest(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="会社１")
        self.category = Category.objects.create(name="カテゴリ１", company=self.company)

    def test_update_not_existed_data(self):
        data = {
            "name": "カテゴリ２"
        }

        response = self.client.put(
            reverse("category-detail", args=[1]),
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_with_invalid_data(self):
        data = {
            "company": 1,
        }

        response = self.client.put(
            reverse("category-detail", args=[str(self.category.id)]),
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_with_valid_data(self):
        data = {
            "name": "あ" * 255
        }

        response = self.client.patch(
            reverse("category-detail", args=[str(self.category.id)]),
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            Category.objects.filter(
                id=self.category.id,
                name="あ" * 255,
            ).exists()
        )

class CategoryViewDeleteTest(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="会社１")
        self.category = Category.objects.create(name="カテゴリ１", company=self.company)

    def test_delete_not_existed_data(self):
        response = self.client.delete(reverse("category-detail", args=[1]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_existed_data(self):
        response = self.client.delete(reverse("category-detail", args=[str(self.category.id)]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Category.objects.filter(
                id=self.category.id,
            ).exists()
        )