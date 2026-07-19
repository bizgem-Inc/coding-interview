from rest_framework.test import APITestCase

from api.models import Category, Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Example Inc.")
        self.category = Category.objects.create(company=self.company, name="Engineering")

    def test_list(self):
        response = self.client.get("/api/categories/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["id"], str(self.category.id))

    def test_retrieve(self):
        response = self.client.get(f"/api/categories/{self.category.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Engineering")

    def test_create(self):
        response = self.client.post(
            "/api/categories/",
            {"company": str(self.company.id), "name": "Product"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(Category.objects.filter(company=self.company, name="Product").exists())

    def test_update(self):
        response = self.client.patch(
            f"/api/categories/{self.category.id}/",
            {"name": "Platform"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Platform")

    def test_destroy(self):
        response = self.client.delete(f"/api/categories/{self.category.id}/")

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())
