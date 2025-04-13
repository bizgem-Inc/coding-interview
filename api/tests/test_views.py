from rest_framework.test import APITestCase
from django.urls import reverse
from api.models.company import Company
from api.models.category import Category

class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Company")
        self.category = Category.objects.create(company=self.company, name="Test Category")
        self.list_url = reverse('category-list')
        self.detail_url = reverse('category-detail', kwargs={'pk': str(self.category.id)})

    def test_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        # 登録済みカテゴリーが1件以上含まれていることを確認
        self.assertGreaterEqual(len(response.data), 1)

    def test_retrieve(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], self.category.name)

    def test_create(self):
        data = {
            "company": self.company.id,
            "name": "New Category",
            "parent_category": None
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], "New Category")


    def test_update(self):
        data = {
            "name": "Updated Category"
        }
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], "Updated Category")

    def test_destroy(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, 204)
        # 削除後に再度詳細取得すると404が返ることを確認
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 404)

    def test_create_category_with_invalid_parent(self):
        """
        異なる`Company`の`parent_category`を指定すると、
        バリデーションエラーが返ることを確認
        """
        another_company = Company.objects.create(name="Another Company")
        other_category = Category.objects.create(company=another_company, name="Other Category")
        data = {
            "company": self.company.id,
            "name": "Invalid Category",
            "parent_category": other_category.id
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("parent_category", response.data)