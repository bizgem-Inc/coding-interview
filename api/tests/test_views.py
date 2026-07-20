from rest_framework import status
from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Company A")
        self.other_company = Company.objects.create(name="Company B")
        self.category = Category.objects.create(company=self.company, name="Category A")

    def test_list(self):
        # 一覧取得で登録済みの全カテゴリが返ることを確認する
        Category.objects.create(company=self.company, name="Category B")

        response = self.client.get("/api/categories/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve(self):
        # IDを指定した単体取得が正しいレコードを返すことを確認する
        response = self.client.get(f"/api/categories/{self.category.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.category.id))
        self.assertEqual(response.data["name"], "Category A")

    def test_retrieve_not_found(self):
        # 存在しないIDを指定した場合は404になることを確認する
        response = self.client.get("/api/categories/00000000-0000-0000-0000-000000000000/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create(self):
        # 必須項目のみで新規作成できることを確認する
        payload = {"company": str(self.company.id), "name": "Category C"}

        response = self.client.post("/api/categories/", payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(company=self.company, name="Category C").exists())

    def test_create_with_parent_category(self):
        # parent_categoryを指定した新規作成で親子関係が保存されることを確認する
        payload = {
            "company": str(self.company.id),
            "name": "Category C",
            "parent_category": str(self.category.id),
        }

        response = self.client.post("/api/categories/", payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Category.objects.get(company=self.company, name="Category C")
        self.assertEqual(created.parent_category_id, self.category.id)

    def test_create_missing_name(self):
        # 必須項目のnameが無い場合は400でエラーになることを確認する
        payload = {"company": str(self.company.id)}

        response = self.client.post("/api/categories/", payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_create_duplicate_name_in_same_company(self):
        # 同一企業内での名前重複はヴァリデーションにより400で弾かれ、
        # 500エラーにならないことを確認する
        payload = {"company": str(self.company.id), "name": "Category A"}

        response = self.client.post("/api/categories/", payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_same_name_in_different_company(self):
        # 一意制約はcompany単位なので、別企業であれば同名でも作成できることを確認する
        payload = {"company": str(self.other_company.id), "name": "Category A"}

        response = self.client.post("/api/categories/", payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_parent_category_from_different_company(self):
        # 他企業のカテゴリを親に指定した場合、企業間でツリーが繋がらないよう400になることを確認する
        other_category = Category.objects.create(company=self.other_company, name="Other Category")
        payload = {
            "company": str(self.company.id),
            "name": "Category C",
            "parent_category": str(other_category.id),
        }

        response = self.client.post("/api/categories/", payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)

    def test_update(self):
        # PUTによる更新で内容が正しく反映されることを確認する
        payload = {"company": str(self.company.id), "name": "Category A Updated"}

        response = self.client.put(f"/api/categories/{self.category.id}/", payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Category A Updated")

    def test_partial_update(self):
        # PATCHによる部分更新で指定したフィールドのみ更新されることを確認する
        response = self.client.patch(f"/api/categories/{self.category.id}/", {"name": "Category A Renamed"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Category A Renamed")

    def test_update_self_parent_category(self):
        # 自分自身を親カテゴリに指定するとツリーが循環するため400になることを確認する
        payload = {
            "company": str(self.company.id),
            "name": "Category A",
            "parent_category": str(self.category.id),
        }

        response = self.client.put(f"/api/categories/{self.category.id}/", payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)

    def test_destroy(self):
        # 削除リクエストでレコードが実際に削除されることを確認する
        response = self.client.delete(f"/api/categories/{self.category.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())
