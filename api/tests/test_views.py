import uuid

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company


class CategoryViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(name="テスト企業1")

    def setUp(self):
        self.category = Category.objects.create(company=self.company, name="食品")

    def test_list(self):
        drink = Category.objects.create(company=self.company, name="飲料")

        response = self.client.get(reverse("category-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            [
                {
                    "id": str(self.category.id),
                    "company": str(self.company.id),
                    "name": "食品",
                    "parent_category": None,
                },
                {
                    "id": str(drink.id),
                    "company": str(self.company.id),
                    "name": "飲料",
                    "parent_category": None,
                },
            ],
        )

    def test_retrieve(self):
        response = self.client.get(reverse("category-detail", args=[self.category.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "id": str(self.category.id),
                "company": str(self.company.id),
                "name": "食品",
                "parent_category": None,
            },
        )

    def test_retrieve_not_found(self):
        response = self.client.get(reverse("category-detail", args=[uuid.uuid4()]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create(self):
        payload = {"company": str(self.company.id), "name": "飲料"}

        response = self.client.post(reverse("category-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Category.objects.filter(company=self.company, name="飲料").exists()
        )

    def test_create_with_parent_category(self):
        payload = {
            "company": str(self.company.id),
            "name": "麺類",
            "parent_category": str(self.category.id),
        }

        response = self.client.post(reverse("category-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Category.objects.get(company=self.company, name="麺類")
        self.assertEqual(created.parent_category, self.category)

    def test_create_without_name(self):
        payload = {"company": str(self.company.id)}

        response = self.client.post(reverse("category-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_create_duplicate_company_and_name(self):
        payload = {"company": str(self.company.id), "name": "食品"}

        response = self.client.post(reverse("category-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertEqual(
            Category.objects.filter(company=self.company, name="食品").count(), 1
        )

    def test_create_with_other_company_parent_category(self):
        other_company = Company.objects.create(name="テスト企業2")
        other_category = Category.objects.create(company=other_company, name="食品")
        payload = {
            "company": str(self.company.id),
            "name": "麺類",
            "parent_category": str(other_category.id),
        }

        response = self.client.post(reverse("category-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)
        self.assertFalse(
            Category.objects.filter(company=self.company, name="麺類").exists()
        )

    def test_update(self):
        payload = {"company": str(self.company.id), "name": "生鮮食品"}

        response = self.client.put(
            reverse("category-detail", args=[self.category.id]), payload, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "生鮮食品")

    def test_partial_update(self):
        response = self.client.patch(
            reverse("category-detail", args=[self.category.id]),
            {"name": "加工食品"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "加工食品")

    def test_update_to_duplicate_company_and_name(self):
        other = Category.objects.create(company=self.company, name="飲料")

        response = self.client.patch(
            reverse("category-detail", args=[other.id]), {"name": "食品"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        other.refresh_from_db()
        self.assertEqual(other.name, "飲料")

    def test_update_parent_category_to_self(self):
        response = self.client.patch(
            reverse("category-detail", args=[self.category.id]),
            {"parent_category": str(self.category.id)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)
        self.category.refresh_from_db()
        self.assertIsNone(self.category.parent_category)

    def test_destroy(self):
        response = self.client.delete(
            reverse("category-detail", args=[self.category.id])
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())
