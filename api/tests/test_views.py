import uuid

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Company, Category


class CategoryViewTests(APITestCase):

    """
    一覧のテスト
    企業のカテゴリーのみ取得できること
    """
    def test_list_success(self):
        # Arrange
        company = Company.objects.create(name="company1")
        Category.objects.create(name="category1-1", company_id=company.id)
        Category.objects.create(name="category1-2", company_id=company.id)

        Category.objects.create(name="category2-1", company_id=Company.objects.create(name="company2").id)

        url = reverse("category-list", kwargs={"company_id": company.id})

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["name"], "category1-1")
        self.assertEqual(response.data[1]["name"], "category1-2")

    """
    一覧のテスト
    存在しない企業IDを指定した場合は404を返す
    """
    def test_list_not_exist_company_failure(self):
        # Arrange
        Company.objects.create(name="company1")

        url = reverse("category-list", kwargs={"company_id": uuid.uuid4()})

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve(self):
        pass

    def test_create(self):
        pass

    def test_update(self):
        pass

    def test_destroy(self):
        pass
