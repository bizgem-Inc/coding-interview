from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Category, Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        # API のテストでは「会社単位の制約」と「参照整合性」が重要になるため、
        # 会社を2つ用意してケース分岐を作る。
        self.company = Company.objects.create(name="Company A")
        self.other_company = Company.objects.create(name="Company B")

        self.list_url = reverse("category-list")

    def _category_detail_url(self, category_id):
        return reverse("category-detail", args=[str(category_id)])

    def test_list(self):
        # 一覧は 200 で返り、作成済みのレコードが含まれることを確認する。
        c1 = Category.objects.create(company=self.company, name="cat1")
        c2 = Category.objects.create(company=self.company, name="cat2")

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        payload = response.json()
        if isinstance(payload, dict) and "results" in payload:
            items = payload["results"]
        else:
            items = payload

        returned_ids = {item["id"] for item in items}
        self.assertTrue(str(c1.id) in returned_ids)
        self.assertTrue(str(c2.id) in returned_ids)

    def test_retrieve(self):
        # 参照は 200 で返り、主キーや company の値が正しくシリアライズされることを確認する。
        category = Category.objects.create(company=self.company, name="cat1")
        response = self.client.get(self._category_detail_url(category.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], str(category.id))
        self.assertEqual(response.json()["name"], "cat1")
        self.assertEqual(response.json()["company"], str(self.company.id))

    def test_create(self):
        # 作成は 201 で返り、レスポンスの内容と DB の永続化が一致することを確認する。
        payload = {"company": str(self.company.id), "name": "cat1"}

        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_id = response.json()["id"]
        self.assertTrue(Category.objects.filter(id=created_id).exists())

        created = Category.objects.get(id=created_id)
        self.assertEqual(created.company_id, self.company.id)
        self.assertEqual(created.name, "cat1")

    def test_update(self):
        # 更新は 200 で返り、PATCH が name を反映することを確認する。
        category = Category.objects.create(company=self.company, name="cat1")
        response = self.client.patch(
            self._category_detail_url(category.id),
            {"name": "cat2"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        category.refresh_from_db()
        self.assertEqual(category.name, "cat2")

    def test_destroy(self):
        # 削除は 204 で返り、レコードが消えていることを確認する。
        category = Category.objects.create(company=self.company, name="cat1")
        response = self.client.delete(self._category_detail_url(category.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=category.id).exists())

    def test_create_unique_violation_returns_400(self):
        # `company + name` がユニーク制約なので、同一条件の再作成は 400 になるべき。
        Category.objects.create(company=self.company, name="cat1")
        response = self.client.post(
            self.list_url,
            {"company": str(self.company.id), "name": "cat1"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_parent_company_mismatch_returns_400(self):
        # 親カテゴリは子と同じ company に属している必要があるため、違反は 400 にする。
        parent = Category.objects.create(company=self.other_company, name="parent")

        response = self.client.post(
            self.list_url,
            {
                "company": str(self.company.id),
                "name": "child",
                "parent_category": str(parent.id),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
