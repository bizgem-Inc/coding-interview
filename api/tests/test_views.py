import uuid
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import Category, Company


class CategoryAPITests(APITestCase):
    """
    カテゴリAPIの全機能を網羅するテスト。
    独自仕様（循環参照防止、削除時の子ID返却、マルチテナント分離）を重点的に検証する。
    """

    @classmethod
    def setUpTestData(cls):
        # テスト用の企業を作成
        cls.company_a = Company.objects.create(id=uuid.uuid4(), name="Company A")
        cls.company_b = Company.objects.create(id=uuid.uuid4(), name="Company B")

        # Company A のカテゴリ階層
        # A_Root
        #   └── A_Child_1
        #       └── A_GrandChild_1
        cls.cat_a_root = Category.objects.create(
            company=cls.company_a, name="A_Root"
        )
        cls.cat_a_child_1 = Category.objects.create(
            company=cls.company_a, name="A_Child_1", parent_category=cls.cat_a_root
        )
        cls.cat_a_grandchild_1 = Category.objects.create(
            company=cls.company_a, name="A_GrandChild_1", parent_category=cls.cat_a_child_1
        )

        # Company B のカテゴリ
        cls.cat_b_root = Category.objects.create(
            company=cls.company_b, name="B_Root"
        )

    def test_list_categories_tree_structure(self):
        """一覧取得時に正しいツリー構造で返却されるか"""
        url = reverse("categories", kwargs={"company_id": self.company_a.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        categories = response.data["categories"]
        
        # A_Rootが1つあり、その中に子がネストされていることを確認
        self.assertEqual(len(categories), 1)
        root = categories[0]
        self.assertEqual(root["name"], "A_Root")
        self.assertEqual(len(root["children"]), 1)
        
        child = root["children"][0]
        self.assertEqual(child["name"], "A_Child_1")
        self.assertEqual(len(child["children"]), 1)

    def test_create_category_with_depth_info(self):
        """新規作成時に親名称や階層深さが正しく返却されるか"""
        url = reverse("categories", kwargs={"company_id": self.company_a.id})
        data = {
            "name": "New Category",
            "parent_category_id": str(self.cat_a_child_1.id)
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["parent_category_name"], "A_Child_1")
        self.assertEqual(response.data["depth"], 2) # Root(0) -> Child(1) -> New(2)

    def test_prevent_circular_reference(self):
        """自分自身や子孫を親に設定しようとした際にブロックされるか"""
        url = reverse(
            "category-detail", 
            kwargs={"company_id": self.company_a.id, "category_id": self.cat_a_root.id}
        )
        # Rootの親を、自分の孫（A_GrandChild_1）に設定しようとする
        data = {"parent_category_id": str(self.cat_a_grandchild_1.id)}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Circular reference detected", str(response.data))

    def test_prevent_other_company_parent(self):
        """他社のカテゴリを親に指定できないこと"""
        url = reverse("categories", kwargs={"company_id": self.company_a.id})
        data = {
            "name": "Evil Category",
            "parent_category_id": str(self.cat_b_root.id) # Company B のカテゴリを指定
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("does not exist within the company", str(response.data))

    def test_delete_category_with_child_ids(self):
        """子を持つカテゴリの削除拒否時に、子IDリストが返却されるか"""
        url = reverse(
            "category-detail", 
            kwargs={"company_id": self.company_a.id, "category_id": self.cat_a_root.id}
        )
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Cannot delete category with children.")
        # 子である A_Child_1 の ID が含まれているか確認
        self.assertIn(self.cat_a_child_1.id, response.data["blocking_child_ids"])

    def test_multi_tenant_isolation(self):
        """他社のカテゴリを詳細取得しようとした際に404になるか"""
        # Company A のパスを使って、Company B のカテゴリを取得しようとする
        url = reverse(
            "category-detail", 
            kwargs={"company_id": self.company_a.id, "category_id": self.cat_b_root.id}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_success(self):
        """子がいないカテゴリは正常に削除できるか"""
        url = reverse(
            "category-detail", 
            kwargs={"company_id": self.company_a.id, "category_id": self.cat_a_grandchild_1.id}
        )
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.cat_a_grandchild_1.id).exists())
