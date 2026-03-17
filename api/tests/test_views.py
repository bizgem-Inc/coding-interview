from rest_framework.test import APITestCase
from django.urls import reverse
from api.models import Company, Category

class CategoryViewTests(APITestCase):
    def setUp(self):
        super().setUp()
        self.company = Company.objects.create(name="テスト企業")
        self.category = Category.objects.create(name="テストカテゴリ", company=self.company)

    def test_list(self):
        url = reverse("category-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "テストカテゴリ")
        self.assertEqual(response.data[0]["company"], self.company.id)
        self.assertIn("created_at", response.data[0])
        self.assertIn("updated_at", response.data[0])

    def test_retrieve(self):
        url = reverse("category-detail", args=[self.category.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "テストカテゴリ")
        self.assertEqual(response.data["company"], self.company.id)
        self.assertEqual(response.data["parent_category"], None)
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data)

    def test_create(self):
        url = reverse("category-list")
        response = self.client.post(url, {"name": "新しいカテゴリ", "company": str(self.company.id)}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "新しいカテゴリ")
        self.assertEqual(response.data["company"], self.company.id)
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data)

    def test_update(self):
        url = reverse("category-detail", args=[self.category.id])
        response = self.client.put(url, {"name": "更新されたカテゴリ", "company": str(self.company.id)}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "更新されたカテゴリ")
        self.assertEqual(response.data["company"], self.company.id)
        self.assertIn("created_at", response.data)


    def test_destroy(self):
        url = reverse("category-detail", args=[self.category.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Category.objects.count(), 0)

    def test_create_with_empty_name_returns_400(self):
        url = reverse("category-list")
        response = self.client.post(
            url, {"name": "", "company": str(self.company.id)}, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_create_with_whitespace_only_name_returns_400(self):
        url = reverse("category-list")
        response = self.client.post(
            url, {"name": "   ", "company": str(self.company.id)}, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_create_with_duplicate_name_in_same_company_returns_400(self):
        url = reverse("category-list")
        response = self.client.post(
            url,
            {"name": "テストカテゴリ", "company": str(self.company.id)},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            "name" in response.data or "non_field_errors" in response.data
        )

    def test_update_with_duplicate_name_in_same_company_returns_400(self):
        Category.objects.create(name="他のカテゴリ", company=self.company)
        url = reverse("category-detail", args=[self.category.id])
        response = self.client.put(
            url,
            {"name": "他のカテゴリ", "company": str(self.company.id)},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            "name" in response.data or "non_field_errors" in response.data
        )
