import uuid

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company


class CategoryListTests(APITestCase):
    LIST_RESPONSE_FIELDS = {"id", "company", "name", "parent_category", "created_at", "updated_at"}

    def setUp(self):
        self.target_company = Company.objects.create(name="Target Company")
        self.non_target_company = Company.objects.create(name="Non Target Company")
        self.target_category1 = Category.objects.create(company=self.target_company, name="Category 1")
        self.target_category2 = Category.objects.create(company=self.target_company, name="Category 2")
        self.non_target_category1 = Category.objects.create(company=self.non_target_company, name="Category 3")

    # 正常系

    def test_list_with_company_filter_returns_multiple_categories(self):
        url = reverse("category-list")

        response = self.client.get(url, {"company": self.target_company.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(set(response.data[0].keys()), self.LIST_RESPONSE_FIELDS)
        returned_ids = {item["id"] for item in response.data}
        self.assertEqual(returned_ids, {str(self.target_category1.id), str(self.target_category2.id)})

    def test_list_with_company_filter_returns_empty_list(self):
        empty_company = Company.objects.create(name="Empty Company")
        url = reverse("category-list")

        response = self.client.get(url, {"company": empty_company.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    # 異常系

    def test_list_without_company_filter_returns_400(self):
        url = reverse("category-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CategoryRetrieveTests(APITestCase):
    DETAIL_RESPONSE_FIELDS = {"id", "company", "name", "parent_category", "created_at", "updated_at"}
    NESTED_COMPANY_FIELDS = {"id", "name"}
    NESTED_CATEGORY_FIELDS = {"id", "name"}

    def setUp(self):
        self.company = Company.objects.create(name="Test Company")
        self.parent_category = Category.objects.create(company=self.company, name="Parent Category")
        self.target_category = Category.objects.create(
            company=self.company, name="Target Category", parent_category=self.parent_category
        )

    # 正常系

    def test_retrieve_returns_category_detail(self):
        url = reverse("category-detail", kwargs={"pk": self.target_category.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), self.DETAIL_RESPONSE_FIELDS)
        self.assertEqual(set(response.data["company"].keys()), self.NESTED_COMPANY_FIELDS)
        self.assertEqual(set(response.data["parent_category"].keys()), self.NESTED_CATEGORY_FIELDS)

    # 異常系

    def test_retrieve_not_found_returns_404(self):
        non_existent_id = uuid.uuid4()
        url = reverse("category-detail", kwargs={"pk": non_existent_id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CategoryCreateTests(APITestCase):
    DETAIL_RESPONSE_FIELDS = {"id", "company", "name", "parent_category", "created_at", "updated_at"}

    def setUp(self):
        self.company = Company.objects.create(name="Test Company")
        self.parent_category = Category.objects.create(company=self.company, name="Parent Category")

    # 正常系

    def test_create_with_parent_category_returns_201(self):
        url = reverse("category-list")
        data = {
            "company": str(self.company.id),
            "name": "New Category",
            "parent_category": str(self.parent_category.id),
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(set(response.data.keys()), self.DETAIL_RESPONSE_FIELDS)
        self.assertEqual(Category.objects.filter(name="New Category").count(), 1)

    def test_create_without_parent_category_returns_201(self):
        url = reverse("category-list")
        data = {
            "company": str(self.company.id),
            "name": "New Category",
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["parent_category"], None)

    # 異常系

    def test_create_without_name_returns_400(self):
        initial_category_count = Category.objects.count()
        url = reverse("category-list")
        data = {"company": str(self.company.id)}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Category.objects.count(), initial_category_count)

    def test_create_with_non_existent_company_returns_400(self):
        initial_category_count = Category.objects.count()
        url = reverse("category-list")
        data = {
            "company": str(uuid.uuid4()),
            "name": "New Category",
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Category.objects.count(), initial_category_count)

    def test_create_with_non_existent_parent_category_returns_400(self):
        initial_category_count = Category.objects.count()
        url = reverse("category-list")
        data = {
            "company": str(self.company.id),
            "name": "New Category",
            "parent_category": str(uuid.uuid4()),
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Category.objects.count(), initial_category_count)

    def test_create_with_duplicate_name_returns_400(self):
        initial_category_count = Category.objects.count()
        url = reverse("category-list")
        data = {
            "company": str(self.company.id),
            "name": "Parent Category",
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Category.objects.count(), initial_category_count)

    def test_create_with_parent_category_from_different_company_returns_400(self):
        other_company = Company.objects.create(name="Other Company")
        other_category = Category.objects.create(company=other_company, name="Other Category")
        initial_category_count = Category.objects.count()
        url = reverse("category-list")
        data = {
            "company": str(self.company.id),
            "name": "New Category",
            "parent_category": str(other_category.id),
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Category.objects.count(), initial_category_count)


class CategoryUpdateTests(APITestCase):
    DETAIL_RESPONSE_FIELDS = {"id", "company", "name", "parent_category", "created_at", "updated_at"}

    def setUp(self):
        self.company = Company.objects.create(name="Test Company")
        self.parent_category = Category.objects.create(company=self.company, name="Parent Category")
        self.target_category = Category.objects.create(company=self.company, name="Target Category")

    # 正常系

    def test_update_returns_200(self):
        url = reverse("category-detail", kwargs={"pk": self.target_category.id})
        data = {
            "name": "Updated Category",
            "parent_category": str(self.parent_category.id),
        }

        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), self.DETAIL_RESPONSE_FIELDS)

        self.target_category.refresh_from_db()
        self.assertEqual(self.target_category.name, "Updated Category")
        self.assertEqual(self.target_category.parent_category, self.parent_category)

    # 異常系

    def test_update_not_found_returns_404(self):
        url = reverse("category-detail", kwargs={"pk": uuid.uuid4()})
        data = {"name": "Updated Category"}

        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_without_name_returns_400(self):
        original_name = self.target_category.name
        url = reverse("category-detail", kwargs={"pk": self.target_category.id})
        data = {}

        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.target_category.refresh_from_db()
        self.assertEqual(self.target_category.name, original_name)

    def test_update_with_self_reference_returns_400(self):
        url = reverse("category-detail", kwargs={"pk": self.target_category.id})
        data = {
            "name": "Updated Category",
            "parent_category": str(self.target_category.id),
        }

        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.target_category.refresh_from_db()
        self.assertIsNone(self.target_category.parent_category)

    def test_update_with_parent_category_from_different_company_returns_400(self):
        other_company = Company.objects.create(name="Other Company")
        other_category = Category.objects.create(company=other_company, name="Other Category")
        url = reverse("category-detail", kwargs={"pk": self.target_category.id})
        data = {
            "name": "Updated Category",
            "parent_category": str(other_category.id),
        }

        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.target_category.refresh_from_db()
        self.assertIsNone(self.target_category.parent_category)

    def test_update_with_duplicate_name_returns_400(self):
        original_name = self.target_category.name
        url = reverse("category-detail", kwargs={"pk": self.target_category.id})
        data = {"name": "Parent Category"}

        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.target_category.refresh_from_db()
        self.assertEqual(self.target_category.name, original_name)


class CategoryDeleteTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Company")
        self.target_category = Category.objects.create(company=self.company, name="Target Category")

    # 正常系

    def test_delete_returns_204(self):
        initial_category_count = Category.objects.count()
        url = reverse("category-detail", kwargs={"pk": self.target_category.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), initial_category_count - 1)
        self.assertFalse(Category.objects.filter(id=self.target_category.id).exists())

    # 異常系

    def test_delete_not_found_returns_404(self):
        initial_category_count = Category.objects.count()
        non_existent_id = uuid.uuid4()
        url = reverse("category-detail", kwargs={"pk": non_existent_id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Category.objects.count(), initial_category_count)
