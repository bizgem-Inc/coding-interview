from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse

from api.models.company import Company
from api.models.category import Category


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Co")
        self.list_url = reverse("category-list")

    def test_list(self):
        Category.objects.create(company=self.company, name="食品")
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve(self):
        category = Category.objects.create(company=self.company, name="食品")
        url = reverse("category-detail", args=[category.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "食品")

    def test_create(self):
        data = {"company": self.company.id, "name": "飲料"}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 1)

    def test_update(self):
        category = Category.objects.create(company=self.company, name="食品")
        url = reverse("category-detail", args=[category.id])
        data = {"company": self.company.id, "name": "飲料"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        category.refresh_from_db()
        self.assertEqual(category.name, "飲料")

    def test_destroy(self):
        category = Category.objects.create(company=self.company, name="食品")
        url = reverse("category-detail", args=[category.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 0)
    
    def test_create_duplicate_name(self):
        # 同じ company × 同じ name は弾かれる（ユニーク制約）
        Category.objects.create(company=self.company, name="食品")
        data = {"company": self.company.id, "name": "食品"}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_parent_from_other_company(self):
        # 別会社のカテゴリを親に指定したら弾かれる
        other_company = Company.objects.create(name="Other Co")
        other_category = Category.objects.create(company=other_company, name="食品")
        data = {
            "company": self.company.id,
            "name": "飲料",
            "parent_category": other_category.id,
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_self_parent(self):
        # 自分自身を親に指定したら弾かれる
        category = Category.objects.create(company=self.company, name="食品")
        url = reverse("category-detail", args=[category.id])
        data = {
            "company": self.company.id,
            "name": "食品",
            "parent_category": category.id,
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)