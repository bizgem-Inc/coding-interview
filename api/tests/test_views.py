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
        url = reverse("category-list", kwargs={"company_id": uuid.uuid4()})

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Company not found")

    """
    詳細のテスト
    企業のカテゴリが取得できること
    """
    def test_retrieve_success(self):
        # Arrange
        company = Company.objects.create(name="company1")
        category = Category.objects.create(name="category1-1", company_id=company.id)

        Category.objects.create(name="category2-1", company_id=Company.objects.create(name="company2").id)

        url = reverse("category-detail", kwargs={"company_id": company.id, "category_id": category.id})

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 6)
        self.assertEqual(uuid.UUID(response.data["id"]), category.id)
        self.assertEqual(response.data["name"], "category1-1")
        self.assertEqual(response.data["company"], company.id)
        self.assertIsNone(response.data["parent_category"])
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data)

    """
    詳細のテスト
    他の企業のカテゴリを指定した場合は404を返す
    """
    def test_retrieve_category_of_another_company_failure(self):
        # Arrange
        company = Company.objects.create(name="company1")
        Category.objects.create(name="category1-1", company_id=company.id)

        another = Category.objects.create(name="category2-1", company_id=Company.objects.create(name="company2").id)

        url = reverse("category-detail", kwargs={
            "company_id": company.id,
            "category_id": another.id, # 別の企業のカテゴリーを指定
        })

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Category not found")

    """
    詳細のテスト
    存在しない企業IDを指定した場合は404を返す
    """
    def test_retrieve_category_not_exist_company_failure(self):
        # Arrange
        company = Company.objects.create(name="company1")
        category = Category.objects.create(name="category1-1", company_id=company.id)

        url = reverse("category-detail", kwargs={
            "company_id": uuid.uuid4(), # 存在しない企業を指定
            "category_id": category.id,
        })

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Company not found")

    """
    詳細のテスト
    存在しないカテゴリIDを指定した場合は404を返す
    """
    def test_retrieve_category_not_exist_category_failure(self):
        # Arrange
        company = Company.objects.create(name="company1")
        Category.objects.create(name="category1-1", company_id=company.id)

        url = reverse("category-detail", kwargs={
            "company_id": company.id,
            "category_id": uuid.uuid4(), # 存在しないカテゴリを指定
        })

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Category not found")

    def test_create(self):
        pass

    def test_update(self):
        pass

    def test_destroy(self):
        pass
