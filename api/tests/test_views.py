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
    企業のカテゴリーが取得できること
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
        self.assertIsNone(response.data["parent_category_id"])
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data)

    """
    詳細のテスト
    他の企業のカテゴリーを指定した場合は404を返す
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
    存在しないカテゴリーIDを指定した場合は404を返す
    """
    def test_retrieve_category_not_exist_category_failure(self):
        # Arrange
        company = Company.objects.create(name="company1")
        Category.objects.create(name="category1-1", company_id=company.id)

        url = reverse("category-detail", kwargs={
            "company_id": company.id,
            "category_id": uuid.uuid4(), # 存在しないカテゴリーを指定
        })

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Category not found")

    """
    新規作成のテスト
    企業のカテゴリーが登録できること
    親カテゴリーは null
    """
    def test_create_success(self):
        # Arrange
        company = Company.objects.create(name="company1")

        url = reverse("category-list", kwargs={"company_id": company.id})
        data = {
            "name": "category1",
            "parent_category_id": None,
        }

        # Act
        response = self.client.post(url, data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Category.objects.count(), 1)

        new_category = Category.objects.first()
        self.assertEqual(new_category.name, "category1")
        self.assertEqual(new_category.company_id, company.id)
        self.assertIsNone(new_category.parent_category)

    """
    新規作成のテスト
    企業のカテゴリーが登録できること
    親カテゴリーがnullではない
    """
    def test_create_store_parent_category_success(self):
        # Arrange
        company = Company.objects.create(name="company1")
        category = Category.objects.create(name="category1-1", company_id=company.id)

        url = reverse("category-list", kwargs={"company_id": company.id})
        data = {
            "name": "category1",
            "parent_category_id": category.id,
        }

        # Act
        response = self.client.post(url, data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Category.objects.count(), 2)

        new_category = Category.objects.exclude(id=category.id).first()
        self.assertEqual(new_category.name, "category1")
        self.assertEqual(new_category.company_id, company.id)
        self.assertEqual(new_category.parent_category_id, category.id)

    """
    新規作成のテスト
    カテゴリー名が重複しても、異なる企業だと登録できること
    """
    def test_create_duplicate_name_success(self):
        # Arrange
        company = Company.objects.create(name="company1")

        another = Category.objects.create(name="category2-1", company_id=Company.objects.create(name="company2").id)

        url = reverse("category-list", kwargs={"company_id": company.id})
        data = {
            "name": "category2-1", # カテゴリー名が重複
            "parent_category_id": None,
        }

        # Act
        response = self.client.post(url, data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Category.objects.count(), 2)

        new_category = Category.objects.exclude(id=another.id).first()
        self.assertEqual(new_category.name, "category2-1")
        self.assertEqual(new_category.company_id, company.id)
        self.assertIsNone(new_category.parent_category_id)

    """
    新規作成のテスト
    同じ企業内でカテゴリー名が重複して登録できないこと
    """
    def test_create_duplicate_name_failure(self):
        # Arrange
        company = Company.objects.create(name="company1")
        category = Category.objects.create(name="category1-1", company_id=company.id)

        url = reverse("category-list", kwargs={"company_id": company.id})
        data = {
            "name": "category1-1", # カテゴリー名が重複
            "parent_category_id": None,
        }

        # Act
        response = self.client.post(url, data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Category name already exists")

    """
    新規作成のテスト
    バリデーションエラー カテゴリー名が空白
    """
    def test_create_name_is_none_validation_error(self):
        # Arrange
        company = Company.objects.create(name="company1")

        url = reverse("category-list", kwargs={"company_id": company.id})
        data = {
            "name": None,
            "parent_category_id": None,
        }

        # Act
        response = self.client.post(url, data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["name"][0], "This field may not be null.")

    """
    新規作成のテスト
    バリデーションエラー カテゴリー名の文字数オーバー
    """
    def test_create_name_validation_error(self):
        # Arrange
        company = Company.objects.create(name="company1")

        url = reverse("category-list", kwargs={"company_id": company.id})
        data = {
            "name": "a" * 256,
            "parent_category_id": None,
        }

        # Act
        response = self.client.post(url, data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["name"][0], "Ensure this field has no more than 255 characters.")

    """
    新規作成のテスト
    存在しない企業IDを指定した場合は404を返す
    """
    def test_create_not_exist_company_failure(self):
        # Arrange
        url = reverse("category-list", kwargs={"company_id": uuid.uuid4()})
        data = {
            "name": "category1",
            "parent_category_id": None,
        }

        # Act
        response = self.client.post(url, data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Company not found")

    """
    新規作成のテスト
    他の企業のカテゴリーを指定した場合は404を返す
    """
    def test_create_parent_category_of_another_company_failure(self):
        # Arrange
        company = Company.objects.create(name="company1")

        another = Category.objects.create(name="category2-1", company_id=Company.objects.create(name="company2").id)

        url = reverse("category-list", kwargs={"company_id": company.id})
        data = {
            "name": "category1",
            "parent_category_id": another.id,
        }

        # Act
        response = self.client.post(url, data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Parent category not found")

    def test_update(self):
        pass

    """
    削除のテスト
    企業のカテゴリーが削除できること
    """
    def test_destroy_success(self):
        # Arrange
        company = Company.objects.create(name="company1")
        category = Category.objects.create(name="category1-1", company_id=company.id)

        url = reverse("category-detail", kwargs={"company_id": company.id, "category_id": category.id})

        # Act
        response = self.client.delete(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(Category.objects.count(), 0)

    """
    削除のテスト
    他の企業のカテゴリーを指定した場合は404を返す
    """
    def test_destroy_category_of_another_company_failure(self):
        # Arrange
        company = Company.objects.create(name="company1")

        another = Category.objects.create(name="category2-1", company_id=Company.objects.create(name="company2").id)

        url = reverse("category-detail", kwargs={
            "company_id": company.id,
            "category_id": another.id, # 別の企業のカテゴリーを指定
        })

        # Act
        response = self.client.delete(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Category not found")

        self.assertEqual(Category.objects.count(), 1)

    """
    削除のテスト
    存在しない企業IDを指定した場合は404を返す
    """
    def test_destroy_category_not_exist_company_failure(self):
        # Arrange
        company = Company.objects.create(name="company1")
        category = Category.objects.create(name="category1-1", company_id=company.id)

        url = reverse("category-detail", kwargs={
            "company_id": uuid.uuid4(), # 存在しない企業を指定
            "category_id": category.id,
        })

        # Act
        response = self.client.delete(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Company not found")

    """
    削除のテスト
    存在しないカテゴリーIDを指定した場合は404を返す
    """
    def test_destroy_category_not_exist_category_failure(self):
        # Arrange
        company = Company.objects.create(name="company1")
        Category.objects.create(name="category1-1", company_id=company.id)

        url = reverse("category-detail", kwargs={
            "company_id": company.id,
            "category_id": uuid.uuid4(), # 存在しないカテゴリーを指定
        })

        # Act
        response = self.client.delete(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Category not found")

    """
    削除のテスト
    子カテゴリーをもつカテゴリーを削除できないこと
    """
    def test_destroy_has_children_category_failure(self):
        # Arrange
        company = Company.objects.create(name="company1")
        parent_category = Category.objects.create(name="category1-1", company_id=company.id) # 削除対象
        Category.objects.create(
            name="category1-2",
            company_id=company.id,
            parent_category_id=parent_category.id
        )

        url = reverse("category-detail", kwargs={
            "company_id": company.id,
            "category_id": parent_category.id,
        })

        # Act
        response = self.client.delete(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Category has child categories")
