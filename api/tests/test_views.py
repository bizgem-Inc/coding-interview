from django.urls import reverse
from rest_framework.fields import DateTimeField
from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company


class CategoryListTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Company")

    def test_list_empty(self):
        """【一覧取得】データが0件のパターン"""
        response = self.client.get(reverse("category-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_list_single(self):
        """【一覧取得】データが1件のパターン"""
        category = Category.objects.create(company=self.company, name="Category 1")
        
        response = self.client.get(reverse("category-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        self.assertEqual(response.data[0]["id"], str(category.id))
        self.assertEqual(response.data[0]["company"], category.company.id)
        self.assertEqual(response.data[0]["name"], "Category 1")
        self.assertIsNone(response.data[0]["parent_category"])
        self.assertEqual(response.data[0]["created_at"], DateTimeField().to_representation(category.created_at))
        self.assertEqual(response.data[0]["updated_at"], DateTimeField().to_representation(category.updated_at))

    def test_list_multiple(self):
        """【一覧取得】データが複数件のパターン"""
        Category.objects.create(company=self.company, name="Category 1")
        Category.objects.create(company=self.company, name="Category 2")
        Category.objects.create(company=self.company, name="Category 3")

        response = self.client.get(reverse("category-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)


class CategoryRetrieveTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Company")
        self.category = Category.objects.create(company=self.company, name="Category")

    def test_retrieve(self):
        """【詳細取得】正常にデータを1件取得できるパターンのテスト"""
        response = self.client.get(reverse("category-detail", args=[self.category.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], str(self.category.id))
        self.assertEqual(response.data["company"], self.category.company.id)
        self.assertEqual(response.data["name"], "Category")
        self.assertIsNone(response.data["parent_category"])

        self.assertEqual(response.data["created_at"], DateTimeField().to_representation(self.category.created_at))
        self.assertEqual(response.data["updated_at"], DateTimeField().to_representation(self.category.updated_at))


class CategoryCreateTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Company")
        self.other_company = Company.objects.create(name="Other Company")
        self.category = Category.objects.create(company=self.company, name="Category")

    def test_create_with_all_fields(self):
        """【登録】すべてのフィールド（オプション含む）を埋めたパターンのテスト"""
        response = self.client.post(
            reverse("category-list"),
            {"company": str(self.company.id), "name": "Child Category", "parent_category": str(self.category.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        created_category = Category.objects.get(id=response.data["id"])
        
        self.assertEqual(response.data["company"], created_category.company.id)
        self.assertEqual(response.data["name"], "Child Category")
        self.assertEqual(response.data["parent_category"], created_category.parent_category.id)
        self.assertEqual(response.data["created_at"], DateTimeField().to_representation(created_category.created_at))
        self.assertEqual(response.data["updated_at"], DateTimeField().to_representation(created_category.updated_at))

        self.assertEqual(created_category.company, self.company)
        self.assertEqual(created_category.name, "Child Category")
        self.assertEqual(created_category.parent_category, self.category)

    def test_create_with_only_required_fields(self):
        """【登録】必須フィールド（company, name）のみでオプション(parent_category)を空にしたパターンのテスト"""
        response = self.client.post(
            reverse("category-list"),
            {"company": str(self.company.id), "name": "Required Only Category"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        created_category = Category.objects.get(id=response.data["id"])

        self.assertEqual(response.data["company"], created_category.company.id)
        self.assertEqual(response.data["name"], "Required Only Category")
        self.assertIsNone(response.data["parent_category"])
        self.assertEqual(response.data["created_at"], DateTimeField().to_representation(created_category.created_at))
        self.assertEqual(response.data["updated_at"], DateTimeField().to_representation(created_category.updated_at))

        self.assertEqual(created_category.company, self.company)
        self.assertEqual(created_category.name, "Required Only Category")
        self.assertIsNone(created_category.parent_category)

    def test_create_with_empty_data(self):
        """【登録】すべてのフィールドを空（未指定）にしたパターンのテスト"""
        response = self.client.post(
            reverse("category-list"),
            {},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("company", response.data)
        self.assertIn("name", response.data)

    def test_create_rejects_duplicate_name_in_same_company(self):
        """【バリデーション】同一企業内で同じ名前のカテゴリ登録を拒否するテスト"""
        response = self.client.post(
            reverse("category-list"),
            {"company": str(self.company.id), "name": self.category.name},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("name", response.data)

    def test_create_rejects_blank_name(self):
        """【バリデーション】名前が空白のみの場合に登録を拒否するテスト"""
        response = self.client.post(
            reverse("category-list"),
            {"company": str(self.company.id), "name": "   "},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("name", response.data)

    def test_create_allows_duplicate_name_in_different_company(self):
        """【バリデーション】別企業であれば同じ名前のカテゴリ登録を許可するテスト"""
        response = self.client.post(
            reverse("category-list"),
            {"company": str(self.other_company.id), "name": self.category.name},
            format="json",
        )

        self.assertEqual(response.status_code, 201)

    def test_create_rejects_parent_category_from_different_company(self):
        """【バリデーション】別企業のカテゴリを親カテゴリとして設定することを拒否するテスト"""
        parent_category = Category.objects.create(company=self.other_company, name="Other Category")

        response = self.client.post(
            reverse("category-list"),
            {"company": str(self.company.id), "name": "Child Category", "parent_category": str(parent_category.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("parent_category", response.data)


class CategoryUpdateTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Company")
        self.other_company = Company.objects.create(name="Other Company")
        self.category = Category.objects.create(company=self.company, name="Category")

    def test_update(self):
        """【更新】正常にデータを更新できるパターンのテスト"""
        parent_category = Category.objects.create(company=self.company, name="Parent Category")

        response = self.client.put(
            reverse("category-detail", args=[self.category.id]),
            {"company": str(self.company.id), "name": "Updated Category", "parent_category": str(parent_category.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.category.refresh_from_db()

        self.assertEqual(response.data["id"], str(self.category.id))
        self.assertEqual(response.data["company"], self.category.company.id)
        self.assertEqual(response.data["name"], "Updated Category")
        self.assertEqual(response.data["parent_category"], self.category.parent_category.id)
        self.assertEqual(response.data["created_at"], DateTimeField().to_representation(self.category.created_at))
        self.assertEqual(response.data["updated_at"], DateTimeField().to_representation(self.category.updated_at))

        self.assertEqual(self.category.name, "Updated Category")
        self.assertEqual(self.category.parent_category, parent_category)

    def test_update_rejects_duplicate_name_in_same_company(self):
        """【バリデーション】更新時、同一企業内で同じ名前への変更を拒否するテスト"""
        other_category = Category.objects.create(company=self.company, name="Other Category")

        response = self.client.patch(
            reverse("category-detail", args=[self.category.id]),
            {"name": other_category.name},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("name", response.data)

    def test_update_allows_same_name_on_same_category(self):
        """【バリデーション】更新時、自分自身の名前をそのまま送信してもエラーにならないテスト"""
        response = self.client.patch(
            reverse("category-detail", args=[self.category.id]),
            {"name": self.category.name},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

    def test_update_rejects_blank_name(self):
        """【バリデーション】更新時、名前を空白のみに変更することを拒否するテスト"""
        response = self.client.patch(
            reverse("category-detail", args=[self.category.id]),
            {"name": "   "},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("name", response.data)

    def test_update_rejects_parent_category_from_different_company(self):
        """【バリデーション】更新時、別企業のカテゴリを親に設定することを拒否するテスト"""
        parent_category = Category.objects.create(company=self.other_company, name="Other Category")

        response = self.client.patch(
            reverse("category-detail", args=[self.category.id]),
            {"parent_category": str(parent_category.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("parent_category", response.data)

    def test_update_rejects_self_parent_category(self):
        """【バリデーション】更新時、自分自身を親カテゴリに設定する（自己参照）ことを拒否するテスト"""
        response = self.client.patch(
            reverse("category-detail", args=[self.category.id]),
            {"parent_category": str(self.category.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("parent_category", response.data)

    def test_update_rejects_descendant_parent_category(self):
        """【バリデーション】更新時、自分の子孫カテゴリを親に設定する（循環参照）ことを拒否するテスト"""
        child_category = Category.objects.create(
            company=self.company,
            name="Child Category",
            parent_category=self.category,
        )
        grandchild_category = Category.objects.create(
            company=self.company,
            name="Grandchild Category",
            parent_category=child_category,
        )

        response = self.client.patch(
            reverse("category-detail", args=[self.category.id]),
            {"parent_category": str(grandchild_category.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("parent_category", response.data)

    def test_update_rejects_company_change_when_child_company_would_not_match(self):
        """【バリデーション】更新時、子カテゴリが存在する場合に企業(company)を変更することを拒否するテスト"""
        Category.objects.create(company=self.company, name="Child Category", parent_category=self.category)

        response = self.client.patch(
            reverse("category-detail", args=[self.category.id]),
            {"company": str(self.other_company.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("company", response.data)


class CategoryDestroyTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Company")
        self.category = Category.objects.create(company=self.company, name="Category")

    def test_destroy(self):
        """【削除】正常にデータを削除できるパターンのテスト"""
        response = self.client.delete(reverse("category-detail", args=[self.category.id]))

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())
