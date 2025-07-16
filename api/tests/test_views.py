from rest_framework.test import APITestCase
from rest_framework import status
from api.models import Company, Category


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="テスト会社")
        self.category1 = Category.objects.create(
            name="カテゴリ1",
            company=self.company
        )
        self.category2 = Category.objects.create(
            name="カテゴリ2",
            company=self.company
        )
    
    def test_list(self):
        """カテゴリ一覧を取得できること"""
        response = self.client.get("/api/categories/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["name"], "カテゴリ1")
        self.assertEqual(response.data[1]["name"], "カテゴリ2")

    def test_retrieve(self):
        """カテゴリ詳細を取得できること"""
        response = self.client.get(f"/api/categories/{self.category1.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.category1.id))
        self.assertEqual(response.data["name"], "カテゴリ1")

    def test_create(self):
        """カテゴリを作成できること"""
        data = {
            "name": "新規カテゴリ",
            "company": str(self.company.id)
        }
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "新規カテゴリ")
        self.assertEqual(Category.objects.count(), 3)

    def test_update(self):
        """カテゴリを更新できること"""
        data = {
            "name": "更新後カテゴリ",
            "company": str(self.company.id)
        }
        response = self.client.put(f"/api/categories/{self.category1.id}/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "更新後カテゴリ")
        
        # DBから再取得して確認
        updated_category = Category.objects.get(pk=self.category1.id)
        self.assertEqual(updated_category.name, "更新後カテゴリ")

    def test_destroy(self):
        """カテゴリを削除できること"""
        response = self.client.delete(f"/api/categories/{self.category1.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 1)
        self.assertFalse(Category.objects.filter(pk=self.category1.id).exists())
    
    def test_create_duplicate_name_in_same_company(self):
        """同一企業内で重複するカテゴリ名は作成できないこと"""
        data = {
            "name": "カテゴリ1",  # 既存のカテゴリと同じ名前
            "company": str(self.company.id)
        }
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Category.objects.count(), 2)  # 増えていないこと
    
    def test_create_same_name_in_different_company(self):
        """異なる企業であれば同じカテゴリ名を作成できること"""
        other_company = Company.objects.create(name="別会社")
        data = {
            "name": "カテゴリ1",  # 既存のカテゴリと同じ名前
            "company": str(other_company.id)
        }
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 3)
    
    def test_create_without_required_fields(self):
        """必須フィールドがない場合はエラーになること"""
        # nameなし
        data = {"company": str(self.company.id)}
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        
        # companyなし
        data = {"name": "新カテゴリ"}
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("company", response.data)
    
    def test_create_with_parent_category(self):
        """親カテゴリを指定してカテゴリを作成できること"""
        data = {
            "name": "子カテゴリ",
            "company": str(self.company.id),
            "parent_category": str(self.category1.id)
        }
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(str(response.data["parent_category"]), str(self.category1.id))
