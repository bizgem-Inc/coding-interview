import uuid

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Company A")
        self.other_company = Company.objects.create(name="Company B")
        self.category = Category.objects.create(company=self.company, name="General")
        self.list_url = reverse("category-list")
        self.detail_url = reverse("category-detail", kwargs={"pk": self.category.id})

    def test_list(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(self.category.id))

    def test_retrieve(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.category.id))

        not_found_url = reverse("category-detail", kwargs={"pk": uuid.uuid4()})
        not_found_response = self.client.get(not_found_url)
        self.assertEqual(not_found_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create(self):
        payload = {"company": str(self.company.id), "name": "Books", "parent_category": None}
        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(company=self.company, name="Books").exists())

        invalid_payload = {"company": str(self.company.id), "name": "   "}
        invalid_response = self.client.post(self.list_url, invalid_payload, format="json")
        self.assertEqual(invalid_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_duplicate_name_returns_400(self):
        duplicate_payload = {"company": str(self.company.id), "name": self.category.name, "parent_category": None}
        response = self.client.post(self.list_url, duplicate_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update(self):
        parent = Category.objects.create(company=self.company, name="Parent")
        payload = {
            "company": str(self.company.id),
            "name": "General Updated",
            "parent_category": str(parent.id),
        }
        response = self.client.put(self.detail_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "General Updated")
        self.assertEqual(self.category.parent_category_id, parent.id)

        invalid_payload = {"parent_category": str(self.category.id)}
        invalid_response = self.client.patch(self.detail_url, invalid_payload, format="json")
        self.assertEqual(invalid_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_cross_company_parent_returns_400(self):
        other_company_parent = Category.objects.create(company=self.other_company, name="Other Parent")
        payload = {"parent_category": str(other_company_parent.id)}
        response = self.client.patch(self.detail_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_destroy(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())
