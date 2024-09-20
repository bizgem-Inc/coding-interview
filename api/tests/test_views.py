from rest_framework.test import APITestCase

from ..models.category import Category
from ..models.company import Company

class CategoryViewTests(APITestCase):
    def setUp(self):
        company1 = Company.objects.create(name="company1")
        company2 = Company.objects.create(name="company2")
        category1 = Category.objects.create(company=company1, name="category1")
        category2 = Category.objects.create(company=company2, name="category2")

    def test_list(self):
        response = self.client.get("/api/categories/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["name"], "category1")
        self.assertEqual(response.data[1]["name"], "category2")

    def test_retrieve(self):
        list_response = self.client.get("/api/categories/")
        id = list_response.data[0]["id"]
        response = self.client.get(f"/api/categories/{id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "category1")

    def test_create(self):
        self.assertEqual(Category.objects.count(), 2)
        company1 = Company.objects.get(name="company1")
        response = self.client.post("/api/categories/", {"company": company1.id, "name": "test_category"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Category.objects.count(), 3)

    def test_update(self):
        category1 = Category.objects.get(name="category1")
        category2 = Category.objects.get(name="category2")
        response = self.client.put(f"/api/categories/{category1.id}/", {"company": category1.company.id, "name": "updated_category", "parent_category": category2.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Category.objects.get(id=category1.id).name, "updated_category")
        self.assertEqual(Category.objects.get(id=category1.id).parent_category, category2)

    def test_destroy(self):
        self.assertEqual(Category.objects.count(), 2)
        category1 = Category.objects.get(name="category1")
        response = self.client.delete(f"/api/categories/{category1.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Category.objects.count(), 1)
