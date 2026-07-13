import uuid
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="テスト企業")
        self.category = Category.objects.create(
            company=self.company,
            name="テストカテゴリ",
        )
        self.category2 = Category.objects.create(
            company=self.company,
            name="テストカテゴリ2",
        )

    def test_list(self):
        # 正常系: カテゴリ一覧の取得
        url = reverse("category-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["name"], "テストカテゴリ")
        self.assertEqual(response.data[1]["name"], "テストカテゴリ2")

    def test_retrieve(self):
        # 正常系: 指定したIDのカテゴリを取得
        url = reverse("category-detail", kwargs={"pk": self.category.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "テストカテゴリ")
        self.assertEqual(response.data["company"], self.company.id)

    def test_create(self):
        # 正常系: カテゴリの作成
        url = reverse("category-list")
        data = {
            "company": self.company.id,
            "name": "新規カテゴリ",
            "parent_category": self.category.id,
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "新規カテゴリ")
        self.assertEqual(response.data["company"], self.company.id)
        self.assertEqual(response.data["parent_category"], self.category.id)

    def test_update(self):
        # 正常系: カテゴリ名の更新
        url = reverse("category-detail", kwargs={"pk": self.category2.id})
        data = {"name": "更新後のカテゴリ名"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "更新後のカテゴリ名")

    def test_destroy(self):
        # 正常系: カテゴリの削除
        url = reverse("category-detail", kwargs={"pk": self.category2.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.category2.id).exists())

    def test_create_validation_empty_name(self):
        # 異常系: カテゴリ名が入力なしの場合、バリデーションエラーになることを確認
        url = reverse("category-list")
        invalid_data = {
            "company": self.company.id,
            "name": " ",
        }
        response = self.client.post(url, invalid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"][0], "This field may not be blank.")

    def test_create_validation_blank_name(self):
        # 異常系: カテゴリ名が空白のみの場合、バリデーションエラーになることを確認
        url = reverse("category-list")
        invalid_data = {
            "company": self.company.id,
            "name": " 　    ",
        }
        response = self.client.post(url, invalid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"][0], "This field may not be blank.")

    def test_create_validate_company_integrity(self):
        # 異常系: 他社のカテゴリを親カテゴリに指定した場合、バリデーションエラーになることを確認
        url = reverse("category-list")
        other_company = Company.objects.create(name="他社")
        other_category = Category.objects.create(
            company=other_company,
            name="他社のカテゴリ",
        )
        invalid_data = {
            "company": self.company.id,
            "name": "無効なカテゴリ",
            "parent_category": other_category.id,
        }
        response = self.client.post(url, invalid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)
        self.assertEqual(response.data["parent_category"][0], "Parent category must belong to the same company.")

    def test_create_validation_duplicate_name(self):
        # 異常系: 同一企業内でカテゴリ名が重複した場合、バリデーションエラーになることを確認
        url = reverse("category-list")
        invalid_data = {
            "company": self.company.id,
            "name": "テストカテゴリ",
        }
        response = self.client.post(url, invalid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertEqual(response.data["non_field_errors"][0], "Category with this name already exists in this company.")

    def test_update_validation_duplicate_name(self):
        # 異常系: 同一企業内でカテゴリ名が重複した場合、バリデーションエラーになることを確認
        url = reverse("category-detail", kwargs={"pk": self.category2.id})
        data = {"name": "テストカテゴリ"}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertEqual(response.data["non_field_errors"][0], "Category with this name already exists in this company.")

    def test_update_validation_company_immutability(self):
        # 異常系: 所属企業(company)を変更しようとした場合、バリデーションエラーになることを確認
        url = reverse("category-detail", kwargs={"pk": self.category2.id})
        other_company = Company.objects.create(name="他社")
        data = {"company": other_company.id}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("company", response.data)
        self.assertEqual(response.data["company"][0], "Company cannot be changed.")

    def test_update_validation_circular_reference_self(self):
        # 異常系: 自分自身を親カテゴリに指定した場合、バリデーションエラーになることを確認
        url = reverse("category-detail", kwargs={"pk": self.category2.id})
        data = {"parent_category": self.category2.id}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)
        self.assertEqual(response.data["parent_category"][0], "Cannot set itself as a parent category.")

    def test_update_validation_circular_reference_descendant(self):
        # 異常系: 子孫カテゴリを親カテゴリに指定した場合、バリデーションエラーになることを確認
        # self.category2 の親を self.category に設定しておく
        self.category2.parent_category = self.category
        self.category2.save()

        # self.category の親に self.category2 を設定しようとする
        url = reverse("category-detail", kwargs={"pk": self.category.id})
        data = {"parent_category": self.category2.id}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)
        self.assertEqual(response.data["parent_category"][0], "Cannot set its descendant as a parent category.")

    def test_update_validation_circular_reference_existing_loop(self):
        # 異常系: 既存データにすでに循環参照が存在し、そこに自身をぶら下げようとした場合のエラーを確認
        category_a = Category.objects.create(company=self.company, name="A")
        category_b = Category.objects.create(company=self.company, name="B", parent_category=category_a)
        category_c = Category.objects.create(company=self.company, name="C", parent_category=category_b)

        # モデルのsave時にエラーとなるため、QuerySet.updateで強制的にループ(C -> A)を作り出す
        Category.objects.filter(id=category_a.id).update(parent_category=category_c)

        # 既存のカテゴリ(self.category)の親を、ループしているツリー(category_a)に設定しようとする
        url = reverse("category-detail", kwargs={"pk": self.category.id})
        data = {"parent_category": category_a.id}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)
        # category_a -> category_c -> category_b -> category_a と辿るため、ループ検知はcategory_aが対象
        self.assertEqual(
            response.data["parent_category"][0],
            "Circular reference detected."
        )
