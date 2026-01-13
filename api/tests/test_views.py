from django.urls import reverse
from rest_framework.test import APITestCase

from api.models import Company, Category


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="テスト企業１")
        self.company_2 = Company.objects.create(name="テスト企業２")
        self.category = Category.objects.create(
            name="テストカテゴリー１", company=self.company
        )
        self.category_2 = Category.objects.create(
            name="テストカテゴリー2", company=self.company_2
        )
        self.category_url = reverse("category-list")

    def test_list(self):
        response = self.client.get(self.category_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["name"], self.category.name)
        self.assertEqual(response.data[0]["company"]["id"], self.company.id)
        self.assertEqual(response.data[0]["company"]["name"], self.company.name)
        self.assertEqual(response.data[1]["name"], self.category_2.name)
        self.assertEqual(response.data[1]["company"]["id"], self.company_2.id)
        self.assertEqual(response.data[1]["company"]["name"], self.company_2.name)

    def test_list_filter_by_company(self):
        response = self.client.get(self.category_url, {"company_id": self.company.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["company"]["id"], self.company.id)

    def test_retrieve(self):
        response = self.client.get(f"{self.category_url}{self.category.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], self.category.name)
        self.assertEqual(response.data["company"]["id"], self.company.id)
        self.assertEqual(response.data["company"]["name"], self.company.name)

    def test_create(self):
        response = self.client.post(
            self.category_url,
            {"name": "テストカテゴリー", "company": self.company.id},
        )
        self.assertEqual(response.status_code, 201)
        new_cat = Category.objects.get(id=response.data["id"])
        self.assertEqual(new_cat.name, "テストカテゴリー")
        self.assertEqual(new_cat.company_id, self.company.id)

    def test_create_with_parent_category(self):
        parent_category = Category.objects.create(
            name="親カテゴリー", company=self.company
        )
        response = self.client.post(
            self.category_url,
            {
                "name": "テストカテゴリー",
                "parent_category": parent_category.id,
                "company": self.company.id,
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "テストカテゴリー")
        self.assertEqual(response.data["parent_category"]["id"], parent_category.id)
        self.assertEqual(response.data["parent_category"]["name"], parent_category.name)
        self.assertEqual(response.data["company"]["id"], self.company.id)
        self.assertEqual(response.data["company"]["name"], self.company.name)

    def test_create_with_parent_category_and_different_company(self):
        response = self.client.post(
            self.category_url,
            {
                "name": "テストカテゴリー",
                "parent_category": self.category.id,
                "company": self.company_2.id,
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            str(response.data["parent_category"][0]),
            "親Categoryと同じCompanyに属している必要があります。",
        )

    def test_update(self):
        response = self.client.patch(
            f"{self.category_url}{self.category.id}/", {"name": "テストカテゴリー"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "テストカテゴリー")
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "テストカテゴリー")

    def test_update_parent_category(self):
        category_3 = Category.objects.create(
            name="テストカテゴリー３", company=self.company
        )
        response = self.client.patch(
            f"{self.category_url}{category_3.id}/",
            {"parent_category": self.category.id},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["parent_category"]["id"], self.category.id)
        self.assertEqual(response.data["parent_category"]["name"], self.category.name)
        self.assertEqual(response.data["company"]["id"], self.company.id)
        self.assertEqual(response.data["company"]["name"], self.company.name)
        category_3.refresh_from_db()
        self.assertEqual(category_3.parent_category_id, self.category.id)

    def test_update_with_parent_category_and_different_company(self):
        response = self.client.patch(
            f"{self.category_url}{self.category.id}/",
            {"parent_category": self.category_2.id},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            str(response.data["parent_category"][0]),
            "親Categoryと同じCompanyに属している必要があります。",
        )

    def test_update_with_self_parent(self):
        response = self.client.patch(
            f"{self.category_url}{self.category.id}/",
            {"parent_category": self.category.id},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            str(response.data["parent_category"][0]),
            "カテゴリは自分自身を親にすることはできません。",
        )

    def test_destroy(self):
        total_cat = Category.objects.count()
        cat_id = self.category.id
        response = self.client.delete(
            f"{self.category_url}{self.category.id}/",
        )
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Category.objects.filter(id=cat_id).exists())
        self.assertEqual(Category.objects.count(), total_cat - 1)

    def test_destroy_parent_nullified(self):
        sample_cat = Category.objects.create(
            name="テストカテゴリー", company=self.company
        )
        response = self.client.delete(
            f"{self.category_url}{self.category.id}/",
        )
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())
        sample_cat.refresh_from_db()
        self.assertIsNone(sample_cat.parent_category)
