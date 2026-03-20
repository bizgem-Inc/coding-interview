from rest_framework.test import APITestCase
from rest_framework import status

from api.models import Company, Category


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company_a = Company.objects.create(name="Company A")
        self.company_b = Company.objects.create(name="Company B")

        self.category_a1 = Category.objects.create(
            company=self.company_a, name="Category A1"
        )
        self.category_a2 = Category.objects.create(
            company=self.company_a,
            name="Category A2",
            parent_category=self.category_a1,
        )
        self.category_b1 = Category.objects.create(
            company=self.company_b, name="Category B1"
        )

    # --- List ---

    def test_list(self):
        response = self.client.get("/api/categories/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        returned_ids = {str(item["id"]) for item in response.data}
        expected_ids = {str(self.category_a1.id), str(self.category_a2.id), str(self.category_b1.id)}
        self.assertEqual(returned_ids, expected_ids)

    def test_list_empty(self):
        Category.objects.all().delete()
        response = self.client.get("/api/categories/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    # --- Retrieve ---

    def test_retrieve(self):
        response = self.client.get(f"/api/categories/{self.category_a1.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.category_a1.id))
        self.assertEqual(response.data["name"], "Category A1")
        self.assertEqual(response.data["company"], self.company_a.id)
        self.assertIsNone(response.data["parent_category"])

    def test_retrieve_not_found(self):
        response = self.client.get("/api/categories/00000000-0000-0000-0000-000000000000/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --- Create ---

    def test_create(self):
        data = {
            "company": str(self.company_a.id),
            "name": "New Category",
        }
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "New Category")
        self.assertEqual(response.data["company"], self.company_a.id)
        self.assertIsNone(response.data["parent_category"])
        self.assertIsNotNone(response.data["created_at"])
        self.assertIsNotNone(response.data["updated_at"])
        self.assertTrue(Category.objects.filter(id=response.data["id"]).exists())

    def test_create_same_name_different_company(self):
        data = {
            "company": str(self.company_b.id),
            "name": "Category A1",
        }
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Category A1")
        self.assertEqual(response.data["company"], self.company_b.id)

    def test_create_with_parent(self):
        data = {
            "company": str(self.company_a.id),
            "name": "Child Category",
            "parent_category": str(self.category_a1.id),
        }
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["parent_category"], self.category_a1.id)

    def test_create_missing_company(self):
        data = {"name": "No Company"}
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("company", response.data)

    def test_create_missing_name(self):
        data = {"company": str(self.company_a.id)}
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_create_empty_name(self):
        data = {"company": str(self.company_a.id), "name": ""}
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_create_name_max_length(self):
        data = {"company": str(self.company_a.id), "name": "a" * 255}
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_name_too_long(self):
        data = {"company": str(self.company_a.id), "name": "a" * 256}
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_create_duplicate_category_name_same_company(self):
        data = {
            "company": str(self.company_a.id),
            "name": "Category A1",
        }
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_nonexistent_company(self):
        data = {
            "company": "00000000-0000-0000-0000-000000000000",
            "name": "Orphan",
        }
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("company", response.data)

    def test_create_nonexistent_parent_category(self):
        data = {
            "company": str(self.company_a.id),
            "name": "Orphan",
            "parent_category": "00000000-0000-0000-0000-000000000000",
        }
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)

    def test_create_parent_from_different_company(self):
        data = {
            "company": str(self.company_a.id),
            "name": "Cross Company",
            "parent_category": str(self.category_b1.id),
        }
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)

    # --- Update ---

    def test_update(self):
        data = {"name": "Updated Name"}
        response = self.client.patch(
            f"/api/categories/{self.category_a1.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Name")

    def test_update_parent_to_null(self):
        data = {"parent_category": None}
        response = self.client.patch(
            f"/api/categories/{self.category_a2.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data["parent_category"])

    def test_update_parent_to_another(self):
        category_a3 = Category.objects.create(
            company=self.company_a, name="Category A3"
        )
        data = {"parent_category": str(category_a3.id)}
        response = self.client.patch(
            f"/api/categories/{self.category_a1.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["parent_category"], category_a3.id)

    def test_update_company_without_children(self):
        # category_b1 は子カテゴリがないので company 変更可
        data = {"company": str(self.company_a.id)}
        response = self.client.patch(
            f"/api/categories/{self.category_b1.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["company"], self.company_a.id)

    def test_update_not_found(self):
        response = self.client.patch(
            "/api/categories/00000000-0000-0000-0000-000000000000/",
            {"name": "X"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_duplicate_name_same_company(self):
        data = {"name": "Category A2"}
        response = self.client.patch(
            f"/api/categories/{self.category_a1.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_company_with_children(self):
        # category_a1 は category_a2 の親なので company 変更不可
        data = {"company": str(self.company_b.id)}
        response = self.client.patch(
            f"/api/categories/{self.category_a1.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("company", response.data)

    def test_update_parent_to_different_company(self):
        data = {"parent_category": str(self.category_b1.id)}
        response = self.client.patch(
            f"/api/categories/{self.category_a1.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)

    def test_update_self_reference(self):
        data = {"parent_category": str(self.category_a1.id)}
        response = self.client.patch(
            f"/api/categories/{self.category_a1.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)

    def test_update_circular_reference(self):
        # category_a1 -> category_a2 -> category_a3 の3ノードチェーンを作り、
        # category_a1 の親を category_a3 に設定すると循環参照になる
        category_a3 = Category.objects.create(
            company=self.company_a, name="Category A3", parent_category=self.category_a2
        )
        data = {"parent_category": str(category_a3.id)}
        response = self.client.patch(
            f"/api/categories/{self.category_a1.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)

    def test_update_company_and_parent_consistent(self):
        # company_b -> company_a に変更しつつ、company_a のカテゴリを親に設定
        data = {
            "company": str(self.company_a.id),
            "parent_category": str(self.category_a1.id),
        }
        response = self.client.patch(
            f"/api/categories/{self.category_b1.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["company"], self.company_a.id)
        self.assertEqual(response.data["parent_category"], self.category_a1.id)

    def test_update_company_and_parent_inconsistent(self):
        # company_b -> company_a に変更しつつ、company_b のカテゴリを親に設定 → 不整合
        category_b2 = Category.objects.create(
            company=self.company_b, name="Category B2"
        )
        data = {
            "company": str(self.company_a.id),
            "parent_category": str(category_b2.id),
        }
        response = self.client.patch(
            f"/api/categories/{self.category_b1.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)

    # --- Delete ---

    def test_destroy(self):
        response = self.client.delete(f"/api/categories/{self.category_a1.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.category_a1.id).exists())

    def test_destroy_not_found(self):
        response = self.client.delete("/api/categories/00000000-0000-0000-0000-000000000000/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_destroy_parent_sets_child_null(self):
        # category_a1 は category_a2 の親。削除すると on_delete=SET_NULL により子の parent_category が NULL になる
        self.client.delete(f"/api/categories/{self.category_a1.id}/")
        self.category_a2.refresh_from_db()
        self.assertIsNone(self.category_a2.parent_category)
