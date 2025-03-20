from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.company import Company
from api.models.category import Category

class CategoryViewTests(APITestCase):
    def setUp(self):
        company = Company.objects.create(name="やまだ自動車")
        self.category_dev = Category.objects.create(name="開発部", company=company)
        self.category_design = Category.objects.create(name="デザイン部", company=company)

    def test_list(self):
        url = reverse("category-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve(self):
        url = reverse("category-detail", args=[self.category_dev.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.category_dev.name)

    def test_create(self):
        pass

    def test_update(self):
        pass

    def test_destroy(self):
        pass
