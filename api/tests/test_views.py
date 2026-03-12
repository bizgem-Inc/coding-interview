from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Category, Company


LIST_URL = "/api/categories/"


def detail_url(category_id):
    return f"/api/categories/{category_id}/"


class CategoryViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(name="Bizgem")
        cls.other_company = Company.objects.create(name="Other Inc")
        cls.parent_category = Category.objects.create(company=cls.company, name="Parent Category")
        cls.category = Category.objects.create(
            company=cls.company,
            name="Child Category",
            parent_category=cls.parent_category,
        )
        cls.other_category = Category.objects.create(company=cls.other_company, name="External Category")

    def test_list(self):
        response = self.client.get(LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(
            [item["name"] for item in response.data],
            ["Child Category", "External Category", "Parent Category"],
        )

    def test_retrieve(self):
        response = self.client.get(detail_url(self.category.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.category.id))
        self.assertEqual(response.data["company"], str(self.company.id))
        self.assertEqual(response.data["name"], "Child Category")
        self.assertEqual(response.data["parent_category"], str(self.parent_category.id))

    def test_create(self):
        payload = {
            "company": str(self.company.id),
            "name": "New Category",
            "parent_category": str(self.parent_category.id),
        }

        response = self.client.post(LIST_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(name="New Category", company=self.company).exists())

        category = Category.objects.get(id=response.data["id"])
        self.assertEqual(category.company_id, self.company.id)
        self.assertEqual(category.parent_category_id, self.parent_category.id)

    def test_create_rejects_duplicate_name_within_company(self):
        payload = {
            "company": str(self.company.id),
            "name": "Child Category",
            "parent_category": str(self.parent_category.id),
        }

        response = self.client.post(LIST_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Category.objects.filter(company=self.company, name="Child Category").count(), 1)

    def test_create_rejects_blank_name(self):
        payload = {
            "company": str(self.company.id),
            "name": "",
            "parent_category": str(self.parent_category.id),
        }

        response = self.client.post(LIST_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Category.objects.filter(company=self.company, name="").exists())

    def test_create_rejects_whitespace_only_name(self):
        payload = {
            "company": str(self.company.id),
            "name": "   ",
            "parent_category": str(self.parent_category.id),
        }

        response = self.client.post(LIST_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_rejects_parent_category_from_another_company(self):
        payload = {
            "company": str(self.company.id),
            "name": "Cross Company Category",
            "parent_category": str(self.other_category.id),
        }

        response = self.client.post(LIST_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Category.objects.filter(company=self.company, name="Cross Company Category").exists())

    def test_update(self):
        payload = {
            "name": "Renamed Category",
            "parent_category": None,
        }

        response = self.client.patch(detail_url(self.category.id), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Renamed Category")
        self.assertIsNone(self.category.parent_category)

    def test_update_rejects_company_change(self):
        payload = {
            "company": str(self.other_company.id),
        }

        response = self.client.patch(detail_url(self.category.id), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.category.refresh_from_db()
        self.assertEqual(self.category.company_id, self.company.id)

    def test_update_rejects_duplicate_name_within_company(self):
        payload = {
            "name": "Parent Category",
        }

        response = self.client.patch(detail_url(self.category.id), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Child Category")

    def test_update_rejects_blank_name(self):
        payload = {
            "name": "",
        }

        response = self.client.patch(detail_url(self.category.id), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_rejects_parent_category_from_another_company(self):
        payload = {
            "parent_category": str(self.other_category.id),
        }

        response = self.client.patch(detail_url(self.category.id), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.category.refresh_from_db()
        self.assertEqual(self.category.parent_category_id, self.parent_category.id)

    def test_destroy(self):
        response = self.client.delete(detail_url(self.category.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())
