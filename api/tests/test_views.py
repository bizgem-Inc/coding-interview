from rest_framework.test import APITestCase
from rest_framework import status

from api.models.company import Company
from api.models.category import Category


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="テスト企業")
        self.category = Category.objects.create(
            company=self.company,
            name="親カテゴリ",
        )

    def test_list(self):
        res = self.client.get("/api/categories/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve(self):
        res = self.client.get(f"/api/categories/{self.category.id}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["name"], "親カテゴリ")
        self.assertEqual(res.data["company"], self.company.id)
        self.assertIsNone(res.data.get("parent_category"))

    def test_create(self):
        payload = {
            "company": str(self.company.id),
            "name": "子カテゴリ",
            "parent_category": str(self.category.id),
        }
        res = self.client.post("/api/categories/", payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)

        # 親子関係の検証を追加
        child = Category.objects.get(id=res.data["id"])
        self.assertEqual(child.parent_category, self.category)
        self.assertEqual(child.company, self.company)

    def test_update(self):
        payload = {"name": "更新後カテゴリ"}
        res = self.client.patch(
            f"/api/categories/{self.category.id}/",
            payload,
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "更新後カテゴリ")

    def test_destroy(self):
        res = self.client.delete(f"/api/categories/{self.category.id}/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 0)

    def test_create_with_blank_name(self):
        """カテゴリ名が空白のみの場合はエラー"""
        payload = {
            "company": str(self.company.id),
            "name": "   ",
        }
        res = self.client.post("/api/categories/", payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", res.data)

    def test_create_duplicate_name_in_same_company(self):
        """同一企業内でカテゴリ名が重複した場合はエラー"""
        payload = {
            "company": str(self.company.id),
            "name": "親カテゴリ",  # 既存と同名
        }
        res = self.client.post("/api/categories/", payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", res.data)

    def test_create_same_name_in_different_company(self):
        """別企業であれば同名カテゴリは作成可能"""
        other_company = Company.objects.create(name="別企業")

        payload = {
            "company": str(other_company.id),
            "name": "親カテゴリ",
        }
        res = self.client.post("/api/categories/", payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_parent_category_from_other_company(self):
        """親カテゴリが別企業の場合はエラー"""
        other_company = Company.objects.create(name="別企業")
        other_category = Category.objects.create(
            company=other_company,
            name="別企業カテゴリ"
        )

        payload = {
            "company": str(self.company.id),
            "name": "不正カテゴリ",
            "parent_category": str(other_category.id),
        }
        res = self.client.post("/api/categories/", payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", res.data)

    def test_update_to_duplicate_name(self):
        """更新時にカテゴリ名を重複させようとするとエラー"""
        Category.objects.create(
            company=self.company,
            name="別カテゴリ"
        )

        payload = {"name": "別カテゴリ"}
        res = self.client.patch(
            f"/api/categories/{self.category.id}/",
            payload,
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", res.data)


    def test_cannot_set_self_as_parent(self):
        """
        自分自身を親カテゴリに指定できない
        """
        payload = {
            "parent_category": str(self.category.id),
        }
        res = self.client.patch(
            f"/api/categories/{self.category.id}/",
            payload,
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "親カテゴリに自身または子孫カテゴリを指定することはできません。",
            str(res.data),
        )

    def test_cannot_set_descendant_as_parent(self):
        """
        子孫カテゴリを親カテゴリに指定できない（多段循環）
        """
        child = Category.objects.create(
            company=self.company,
            name="子カテゴリ",
            parent_category=self.category,
        )
        grandchild = Category.objects.create(
            company=self.company,
            name="孫カテゴリ",
            parent_category=child,
        )

        payload = {
            "parent_category": str(grandchild.id),
        }
        res = self.client.patch(
            f"/api/categories/{self.category.id}/",
            payload,
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "親カテゴリに自身または子孫カテゴリを指定することはできません。",
            str(res.data),
        )

    def test_retrieve_nonexistent(self):
        """存在しないIDで404"""
        res = self.client.get("/api/categories/99999/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_with_children(self):
        """子カテゴリがある場合、親を削除すると子の parent_category は null になる"""
        child = Category.objects.create(
            company=self.company,
            name="子カテゴリ",
            parent_category=self.category,
        )

        res = self.client.delete(f"/api/categories/{self.category.id}/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        # 親カテゴリは削除されている
        self.assertFalse(
            Category.objects.filter(id=self.category.id).exists()
        )

        # 子カテゴリは残っており、parent_category が null になっている
        child.refresh_from_db()
        self.assertIsNone(child.parent_category)
        self.assertEqual(child.company, self.company)