from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models.category import Category
from api.models.company import Company

class CategoryAPITests(APITestCase):
    def setUp(self):
        """テスト開始前の共通データ準備"""
        # 1. 会社を2つ作成
        self.company_a = Company.objects.create(name="A社")
        self.company_b = Company.objects.create(name="B社")

        # 2. 最初から存在する親カテゴリ（A社所属）を作成
        self.parent_cat = Category.objects.create(
            name="家電",
            company=self.company_a
        )

        self.list_url = reverse('category-list')

    # --- C: Create (作成) のテスト ---
    def test_create_category_success(self):
        """正常系：新しいカテゴリを正常に作成できること"""
        data = {
            "name": "冷蔵庫",
            "company": self.company_a.id,
            "parent_category": self.parent_cat.id
        }
        response = self.client.post(self.list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # setUpの1件 + 今回の1件 = 合計2件
        self.assertEqual(Category.objects.count(), 2)
        self.assertEqual(response.data['name'], "冷蔵庫")

    def test_create_category_duplicate_name_error(self):
        """異常系：同じ会社内で同名のカテゴリは作成できないこと（一意性制約）"""
        data = {
            "name": "家電", # すでにA社にある名前
            "company": self.company_a.id
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_category_different_company_parent_error(self):
        """異常系：別会社のカテゴリを親に設定しようとするとバリデーションエラーになること"""
        data = {
            "name": "B社の家電",
            "company": self.company_b.id, # B社として作成
            "parent_category": self.parent_cat.id # 親はA社のカテゴリを指定
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)

    # --- R: Read (読み取り) のテスト ---
    def test_get_category_list(self):
        """正常系：カテゴリ一覧を取得できること"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # setUpで作った1件が返ってくる
        self.assertEqual(len(response.data), 1)

    # --- U: Update (更新) のテスト ---
    def test_update_category_name(self):
        """正常系：カテゴリ名を変更できること"""
        url = reverse('category-detail', args=[self.parent_cat.id])
        data = {"name": "キッチン家電"}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.parent_cat.refresh_from_db()
        self.assertEqual(self.parent_cat.name, "キッチン家電")

    def test_prevent_self_parenting(self):
        """異常系：自分自身を親に設定できないこと"""
        url = reverse('category-detail', args=[self.parent_cat.id])
        data = {"parent_category": self.parent_cat.id}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- D: Delete (削除) のテスト ---
    def test_delete_parent_category_safe(self):
        """正常系：親を削除しても子が連鎖削除されず、親項目が空になること"""
        # 子カテゴリを作成しておく
        child = Category.objects.create(
            name="炊飯器",
            company=self.company_a,
            parent_category=self.parent_cat
        )

        url = reverse('category-detail', args=[self.parent_cat.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # 親は消えたが、子は残っている（計1件）
        self.assertEqual(Category.objects.count(), 1)
        child.refresh_from_db()
        self.assertIsNone(child.parent_category)