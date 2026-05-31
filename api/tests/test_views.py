from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Company")
        self.category = Category.objects.create(company=self.company, name="Test Category")
        self.list_url = reverse("category-list")
        self.detail_url = reverse("category-detail", kwargs={"pk": self.category.pk})

    def test_list(self):
        response = self.client.get(self.list_url, {"company": self.company.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Test Category")

    def test_list_without_company(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Category")

    def test_create(self):
        data = {
            "company": self.company.pk,
            "name": "New Category"
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)
        self.assertEqual(response.data["name"], "New Category")

    def test_update(self):
        data = {
            "company": self.company.pk,
            "name": "Updated Category"
        }
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Updated Category")

    def test_destroy(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 0)

    def test_e2e_scenario(self):
        """
        E2E統合シナリオ:
        - create：親カテゴリと子カテゴリを連続で追加
        - read：作成したカテゴリが取得でき、親子関係が設定されていること
        - update：親カテゴリを更新
        - delete (error)：子のいる親を削除しようとしてエラーになること
        - delete (success)：子カテゴリを削除し、その後親カテゴリも削除できること
        """
        Category.objects.all().delete()
        
        # 1. create (親カテゴリと子カテゴリを追加)
        resp1 = self.client.post(self.list_url, {"company": self.company.pk, "name": "Cat 1 (Parent)"})
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)
        cat1_id = resp1.data["id"]

        resp2 = self.client.post(self.list_url, {
            "company": self.company.pk, 
            "name": "Cat 2 (Child)",
            "parent_category": cat1_id
        })
        self.assertEqual(resp2.status_code, status.HTTP_201_CREATED)
        cat2_id = resp2.data["id"]

        # 2. read (取得して親子関係の確認)
        resp_read = self.client.get(self.list_url, {"company": self.company.pk})
        self.assertEqual(resp_read.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp_read.data), 2)
        child_data = next(cat for cat in resp_read.data if cat["id"] == cat2_id)
        self.assertEqual(str(child_data["parent_category"]), str(cat1_id))

        # 3. update (親カテゴリの更新)
        detail_url1 = reverse("category-detail", kwargs={"pk": cat1_id})
        resp_update = self.client.put(detail_url1, {"company": self.company.pk, "name": "Cat 1 Updated"})
        self.assertEqual(resp_update.status_code, status.HTTP_200_OK)

        # 4. delete (子のいる親の削除エラー)
        resp_del_parent_error = self.client.delete(detail_url1)
        self.assertEqual(resp_del_parent_error.status_code, status.HTTP_400_BAD_REQUEST)

        # 5. delete (子カテゴリの削除 -> 成功)
        detail_url2 = reverse("category-detail", kwargs={"pk": cat2_id})
        resp_del_child = self.client.delete(detail_url2)
        self.assertEqual(resp_del_child.status_code, status.HTTP_204_NO_CONTENT)

        # 一覧取得で親のみ残っていることを確認
        resp_final = self.client.get(self.list_url, {"company": self.company.pk})
        self.assertEqual(len(resp_final.data), 1)
        self.assertEqual(resp_final.data[0]["name"], "Cat 1 Updated")

        # 6. delete (子が無くなった親の削除 -> 成功)
        resp_del_parent_success = self.client.delete(detail_url1)
        self.assertEqual(resp_del_parent_success.status_code, status.HTTP_204_NO_CONTENT)
