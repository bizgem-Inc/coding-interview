from django.conf import settings
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
    
    def test_create_deep_hierarchy(self):
        """3階層のカテゴリ構造を作成できること"""
        # 子カテゴリを作成
        child_data = {
            "name": "子カテゴリ",
            "company": str(self.company.id),
            "parent_category": str(self.category1.id)
        }
        child_response = self.client.post("/api/categories/", child_data, format="json")
        self.assertEqual(child_response.status_code, status.HTTP_201_CREATED)
        child_id = child_response.data["id"]
        
        # 孫カテゴリを作成
        grandchild_data = {
            "name": "孫カテゴリ",
            "company": str(self.company.id),
            "parent_category": str(child_id)
        }
        grandchild_response = self.client.post("/api/categories/", grandchild_data, format="json")
        self.assertEqual(grandchild_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(str(grandchild_response.data["parent_category"]), str(child_id))
    
    def test_update_parent_category_different_company(self):
        """更新時に異なる企業のカテゴリを親に設定できないこと"""
        other_company = Company.objects.create(name="別会社")
        other_category = Category.objects.create(
            name="別会社カテゴリ",
            company=other_company
        )
        
        data = {
            "name": self.category1.name,
            "company": str(self.company.id),
            "parent_category": str(other_category.id)
        }
        response = self.client.put(f"/api/categories/{self.category1.id}/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)
    
    def test_access_nonexistent_resource(self):
        """存在しないリソースへのアクセスで404が返ること"""
        import uuid
        nonexistent_id = uuid.uuid4()
        
        # 詳細取得
        response = self.client.get(f"/api/categories/{nonexistent_id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # 更新
        data = {"name": "更新", "company": str(self.company.id)}
        response = self.client.put(f"/api/categories/{nonexistent_id}/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # 削除
        response = self.client.delete(f"/api/categories/{nonexistent_id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_validate_name_max_length(self):
        """カテゴリ名が最大文字数を超える場合はエラーになること"""
        max_length = getattr(settings, 'CATEGORY_NAME_MAX_LENGTH', 255)
        data = {
            "name": "あ" * (max_length + 1),  # 最大文字数+1
            "company": str(self.company.id)
        }
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        # DjangoのCharFieldが自動的にmax_lengthをチェックする
        self.assertTrue(
            f"{max_length}文字以内" in str(response.data["name"]) or 
            "no more than 255 characters" in str(response.data["name"])
        )
    
    def test_prevent_self_reference(self):
        """自分自身を親カテゴリに設定できないこと"""
        data = {
            "name": self.category1.name,
            "company": str(self.company.id),
            "parent_category": str(self.category1.id)  # 自分自身
        }
        response = self.client.put(f"/api/categories/{self.category1.id}/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)
        self.assertIn("自分自身", str(response.data["parent_category"]))
    
    def test_max_depth_validation(self):
        """4階層目のカテゴリは作成できないこと"""
        # 子カテゴリを作成（2階層目）
        child = Category.objects.create(
            name="子カテゴリ",
            company=self.company,
            parent_category=self.category1
        )
        
        # 孫カテゴリを作成（3階層目）
        grandchild = Category.objects.create(
            name="孫カテゴリ",
            company=self.company,
            parent_category=child
        )
        
        # 曾孫カテゴリを作成しようとする（4階層目）
        data = {
            "name": "曾孫カテゴリ",
            "company": str(self.company.id),
            "parent_category": str(grandchild.id)
        }
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)
        max_depth = getattr(settings, 'CATEGORY_MAX_DEPTH', 3)
        self.assertIn(f"{max_depth}階層まで", str(response.data["parent_category"]))
