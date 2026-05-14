from rest_framework import status
from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company


class CategoryViewTests(APITestCase):
    def test_list(self):
        company = Company.objects.create(name="Test1")
        Category.objects.create(company=company, name="開発")

        response = self.client.get("/api/categories/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "開発")

    def test_retrieve(self):
        company = Company.objects.create(name="Test1")
        category = Category.objects.create(company=company, name="開発")

        response = self.client.get(f"/api/categories/{category.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(category.id))
        self.assertEqual(response.data["name"], "開発")

    def test_create(self):
        company = Company.objects.create(name="Test1")

        response = self.client.post(
         "/api/categories/",
         {
             "company": str(company.id),
             "name": "開発",
             "parent_category": None,
         },
         format="json",
    )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(Category.objects.get().name, "開発")

    def test_update(self):
        company = Company.objects.create(name="Test1")
        category = Category.objects.create(company=company, name="開発")

        response = self.client.patch(
            f"/api/categories/{category.id}/",
            {"name": "開発2"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        category.refresh_from_db()
        self.assertEqual(category.name, "開発2")

    def test_destroy(self):
        company = Company.objects.create(name="Test1")
        category = Category.objects.create(company=company, name="開発")

        response = self.client.delete(f"/api/categories/{category.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=category.id).exists())
