import uuid

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Category, Company


class CategoryViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(name="テスト企業")
        cls.other_company = Company.objects.create(name="別のテスト企業")

    @property
    def list_url(self):
        return reverse("category-list")

    def detail_url(self, category_id):
        return reverse("category-detail", args=[category_id])

    # 読み取り(一覧)

    def test_list(self):
        """一覧APIは登録済みのカテゴリをcreated_at順で返す。"""
        first = Category.objects.create(company=self.company, name="家電")
        second = Category.objects.create(company=self.other_company, name="書籍")

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([str(item["id"]) for item in response.data], [str(first.id), str(second.id)])

    def test_list_returns_empty_list_when_no_category(self):
        """カテゴリが1件もない場合は空配列を返す。"""
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    # 読み取り(詳細)

    def test_retrieve(self):
        """詳細APIは指定したカテゴリの全フィールドを返す。"""
        parent = Category.objects.create(company=self.company, name="家電")
        category = Category.objects.create(company=self.company, name="テレビ", parent_category=parent)

        response = self.client.get(self.detail_url(category.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data["id"]), str(category.id))
        self.assertEqual(str(response.data["company"]), str(self.company.id))
        self.assertEqual(response.data["name"], "テレビ")
        self.assertEqual(str(response.data["parent_category"]), str(parent.id))
        self.assertIsNotNone(response.data["created_at"])
        self.assertIsNotNone(response.data["updated_at"])

    def test_retrieve_not_found(self):
        """存在しないidを指定した場合は404を返す。"""
        response = self.client.get(self.detail_url(uuid.uuid4()))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # 作成

    def test_create(self):
        """作成APIはカテゴリを新規登録し、201を返す。"""
        payload = {"company": str(self.company.id), "name": "家電"}

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        category = Category.objects.get(id=response.data["id"])
        self.assertEqual(category.name, "家電")
        self.assertEqual(category.company_id, self.company.id)
        self.assertIsNone(category.parent_category)

    def test_create_with_parent_category(self):
        """親カテゴリを指定して子カテゴリを作成できる。"""
        parent = Category.objects.create(company=self.company, name="家電")
        payload = {"company": str(self.company.id), "name": "テレビ", "parent_category": str(parent.id)}

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.get(id=response.data["id"]).parent_category_id, parent.id)

    def test_create_without_required_fields(self):
        """company・nameが未指定の場合は400を返し、作成されない。"""
        response = self.client.post(self.list_url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("company", response.data)
        self.assertIn("name", response.data)
        self.assertEqual(Category.objects.count(), 0)

    def test_create_with_max_length_name(self):
        """nameの上限である255文字ちょうどは登録できる。"""
        payload = {"company": str(self.company.id), "name": "あ" * 255}

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(Category.objects.get(id=response.data["id"]).name), 255)

    def test_create_with_too_long_name(self):
        """256文字は400を返す(バイト数ではなく文字数で判定される)。"""
        payload = {"company": str(self.company.id), "name": "あ" * 256}

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(Category.objects.count(), 0)

    def test_create_with_blank_name(self):
        """空文字のnameは400を返す。"""
        payload = {"company": str(self.company.id), "name": ""}

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(Category.objects.count(), 0)

    def test_create_duplicate_name_in_same_company(self):
        """同一企業内で重複するカテゴリ名は400を返す(DBエラーにしない)。"""
        Category.objects.create(company=self.company, name="家電")
        payload = {"company": str(self.company.id), "name": "家電"}

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Category.objects.count(), 1)

    def test_create_same_name_in_other_company(self):
        """企業が異なれば同じカテゴリ名を登録できる。"""
        Category.objects.create(company=self.company, name="家電")
        payload = {"company": str(self.other_company.id), "name": "家電"}

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)

    def test_create_with_parent_category_of_other_company(self):
        """他企業のカテゴリを親に指定した場合は400を返す。"""
        parent = Category.objects.create(company=self.other_company, name="家電")
        payload = {"company": str(self.company.id), "name": "テレビ", "parent_category": str(parent.id)}

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)

    # 更新

    def test_update(self):
        """更新API(PUT)はカテゴリを置き換える。"""
        parent = Category.objects.create(company=self.company, name="家電")
        category = Category.objects.create(company=self.company, name="テレビ", parent_category=parent)
        payload = {"company": str(self.company.id), "name": "液晶テレビ", "parent_category": None}

        response = self.client.put(self.detail_url(category.id), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        category.refresh_from_db()
        self.assertEqual(category.name, "液晶テレビ")
        self.assertIsNone(category.parent_category)

    def test_partial_update(self):
        """更新API(PATCH)は指定したフィールドのみ更新する。"""
        parent = Category.objects.create(company=self.company, name="家電")
        category = Category.objects.create(company=self.company, name="テレビ", parent_category=parent)

        response = self.client.patch(self.detail_url(category.id), {"name": "液晶テレビ"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        category.refresh_from_db()
        self.assertEqual(category.name, "液晶テレビ")
        self.assertEqual(category.parent_category_id, parent.id)

    def test_partial_update_to_duplicate_name(self):
        """同一企業内の既存カテゴリと同名に変更しようとした場合は400を返す。"""
        Category.objects.create(company=self.company, name="家電")
        category = Category.objects.create(company=self.company, name="書籍")

        response = self.client.patch(self.detail_url(category.id), {"name": "家電"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        category.refresh_from_db()
        self.assertEqual(category.name, "書籍")

    def test_partial_update_with_same_name(self):
        """自分自身と同じ名前での更新は一意制約に抵触しない。"""
        category = Category.objects.create(company=self.company, name="家電")

        response = self.client.patch(self.detail_url(category.id), {"name": "家電"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_update_with_self_as_parent_category(self):
        """自分自身を親カテゴリに指定した場合は400を返す。"""
        category = Category.objects.create(company=self.company, name="家電")

        response = self.client.patch(
            self.detail_url(category.id), {"parent_category": str(category.id)}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)

    def test_partial_update_with_descendant_as_parent_category(self):
        """子孫カテゴリを親に指定した場合は循環参照となるため400を返す。"""
        parent = Category.objects.create(company=self.company, name="家電")
        child = Category.objects.create(company=self.company, name="テレビ", parent_category=parent)
        grandchild = Category.objects.create(company=self.company, name="液晶テレビ", parent_category=child)

        response = self.client.patch(
            self.detail_url(parent.id), {"parent_category": str(grandchild.id)}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        parent.refresh_from_db()
        self.assertIsNone(parent.parent_category)

    def test_update_rejects_company_change(self):
        """所属企業の変更は400を返す。"""
        category = Category.objects.create(company=self.company, name="家電")

        response = self.client.patch(
            self.detail_url(category.id), {"company": str(self.other_company.id)}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("company", response.data)
        category.refresh_from_db()
        self.assertEqual(category.company_id, self.company.id)

    def test_update_company_change_does_not_orphan_child(self):
        """所属企業を変更できないため、子が企業を跨いだ親を持つ状態にはならない。"""
        parent = Category.objects.create(company=self.company, name="家電")
        child = Category.objects.create(company=self.company, name="テレビ", parent_category=parent)

        response = self.client.patch(
            self.detail_url(parent.id), {"company": str(self.other_company.id)}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        child.refresh_from_db()
        self.assertEqual(child.company_id, child.parent_category.company_id)

    def test_update_not_found(self):
        """存在しないidの更新は404を返す。"""
        payload = {"company": str(self.company.id), "name": "家電"}

        response = self.client.put(self.detail_url(uuid.uuid4()), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # 削除

    def test_destroy(self):
        """削除APIはカテゴリを削除し、204を返す。"""
        category = Category.objects.create(company=self.company, name="家電")

        response = self.client.delete(self.detail_url(category.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=category.id).exists())

    def test_destroy_keeps_child_category(self):
        """親カテゴリを削除しても子カテゴリは残り、parent_categoryがNULLになる。"""
        parent = Category.objects.create(company=self.company, name="家電")
        child = Category.objects.create(company=self.company, name="テレビ", parent_category=parent)

        response = self.client.delete(self.detail_url(parent.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        child.refresh_from_db()
        self.assertIsNone(child.parent_category)

    def test_destroy_not_found(self):
        """存在しないidの削除は404を返す。"""
        response = self.client.delete(self.detail_url(uuid.uuid4()))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
