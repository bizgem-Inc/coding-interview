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
        response = self.client.get(f"/api/categories/?company={self.target_company.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(set(response.data[0].keys()), self.LIST_RESPONSE_FIELDS)
        returned_ids = {item["id"] for item in response.data}
        self.assertEqual(returned_ids, {str(self.target_category1.id), str(self.target_category2.id)})

    def test_list_with_company_filter_returns_empty_list(self):
        empty_company = Company.objects.create(name="Empty Company")

        response = self.client.get(f"/api/categories/?company={empty_company.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    # 異常系

    def test_list_without_company_filter_returns_400(self):
        response = self.client.get("/api/categories/")

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
        response = self.client.get(f"/api/categories/{self.target_category.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), self.DETAIL_RESPONSE_FIELDS)
        self.assertEqual(set(response.data["company"].keys()), self.NESTED_COMPANY_FIELDS)
        self.assertEqual(set(response.data["parent_category"].keys()), self.NESTED_CATEGORY_FIELDS)

    # 異常系

    def test_retrieve_not_found_returns_404(self):
        import uuid

        non_existent_id = uuid.uuid4()

        response = self.client.get(f"/api/categories/{non_existent_id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
