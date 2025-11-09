from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Company, Category


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Company")
        self.parent = Category.objects.create(
            company=self.company,
            name="Parent",
        )
        self.child = Category.objects.create(
            company=self.company,
            name="Child",
            parent_category=self.parent,
        )

    def test_list(self):
        url = reverse("category-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Categoryが2件返ってくることを確認
        self.assertEqual(len(response.data), 2)
        names = {item["name"] for item in response.data}
        self.assertSetEqual(names, {"Parent", "Child"})

    def test_retrieve(self):
        url = reverse("category-detail", args=[self.child.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.child.id))
        self.assertEqual(response.data["name"], "Child")
        self.assertEqual(response.data["company"], str(self.company.id))
        self.assertEqual(response.data["parent_category"], str(self.parent.id))

    def test_create(self):
        url = reverse("category-list")
        data = {
            "company": str(self.company.id),
            "name": "New Category",
            "parent_category": str(self.parent.id),
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(name="New Category").exists())

    def test_update(self):
        url = reverse("category-detail", args=[self.child.id])
        data = {
            "company": str(self.company.id),
            "name": "Updated Child",
            "parent_category": str(self.parent.id),
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.child.refresh_from_db()
        self.assertEqual(self.child.name, "Updated Child")

    def test_destroy(self):
        url = reverse("category-detail", args=[self.child.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.child.id).exists())
