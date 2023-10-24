import json
from rest_framework.test import APITestCase
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_422_UNPROCESSABLE_ENTITY
from domain.service.category import CategoryDomainService


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.service = CategoryDomainService()
        self.category_1 = self.service.create("Test Category1", None, "Test Company1")
        self.category_2 = self.service.create("Test Category2", None, "Test Company2")

    def test_list(self):
        """
        レスポンスが正しいことを確認
        """
        response = self.client.get("/api/category/list")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertTrue("entities" in response.data)

    def test_retrieve(self):
        """
        レスポンスが正しいことを確認
        """
        response = self.client.get(f"/api/category/get/{self.category_1.id}")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertTrue("entity" in response.data)

    def test_retrieve_not_found(self):
        """
        存在しない場合には404が返ることを確認
        """
        response = self.client.get(f"/api/category/get/c6047111-04d8-4f57-ba66-da2eff154a7e")
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_create(self):
        """
        レスポンスが正しいことを確認
        """
        data = {
            "name": "New Category",
            "company": {"name": "New Company"}
        }
        response = self.client.post("/api/category/create", data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_create_validation_error(self):
        """
        バリデーションエラーの場合には422が返ることを確認
        """
        data = {
            "not_name": "New Category",
            "company": {"name": "New Company"}
        }
        response = self.client.post("/api/category/create", data, format="json")
        self.assertEqual(response.status_code, HTTP_422_UNPROCESSABLE_ENTITY)

    def test_update(self):
        """
        レスポンスが正しいことを確認
        """
        data = {
            "id": self.category_1.id,
            "name": "Updated Category",
        }
        response = self.client.put(f"/api/category/update", data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_update_not_found(self):
        """
        存在しない場合には404が返ることを確認
        """
        data = {
            "id": "c6047111-04d8-4f57-ba66-da2eff154a7e",
            "name": "Updated Category",
        }
        response = self.client.put(f"/api/category/update", data, format="json")
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_update_validation_error(self):
        """
        バリデーションエラーの場合には422が返ることを確認
        """
        data = {
            "id": self.category_1.id,
            "not_name": "Updated Category",
        }
        response = self.client.put(f"/api/category/update", data, format="json")
        self.assertEqual(response.status_code, HTTP_422_UNPROCESSABLE_ENTITY)

    def test_destroy(self):
        """
        レスポンスが正しいことを確認
        """
        response = self.client.delete(f"/api/category/delete/{self.category_1.id}")
        self.assertEqual(response.status_code, HTTP_200_OK)
