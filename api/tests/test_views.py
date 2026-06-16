from django.urls import reverse
from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Company")
        self.other_company = Company.objects.create(name="Other Company")
        self.category = Category.objects.create(company=self.company, name="Category")

    def test_list(self):
        response = self.client.get(reverse("category-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(self.category.id))
        self.assertEqual(response.data[0]["company"], self.company.id)
        self.assertEqual(response.data[0]["name"], "Category")
        self.assertIsNone(response.data[0]["parent_category"])

    def test_retrieve(self):
        response = self.client.get(reverse("category-detail", args=[self.category.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], str(self.category.id))
        self.assertEqual(response.data["name"], "Category")

    def test_create(self):
        response = self.client.post(
            reverse("category-list"),
            {"company": str(self.company.id), "name": "Child Category", "parent_category": str(self.category.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        created_category = Category.objects.get(id=response.data["id"])
        self.assertEqual(created_category.company, self.company)
        self.assertEqual(created_category.name, "Child Category")
        self.assertEqual(created_category.parent_category, self.category)

    def test_update(self):
        parent_category = Category.objects.create(company=self.company, name="Parent Category")

        response = self.client.put(
            reverse("category-detail", args=[self.category.id]),
            {"company": str(self.company.id), "name": "Updated Category", "parent_category": str(parent_category.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Updated Category")
        self.assertEqual(self.category.parent_category, parent_category)

    def test_destroy(self):
        response = self.client.delete(reverse("category-detail", args=[self.category.id]))

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())

    def test_create_rejects_duplicate_name_in_same_company(self):
        response = self.client.post(
            reverse("category-list"),
            {"company": str(self.company.id), "name": self.category.name},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("name", response.data)

    def test_create_rejects_blank_name(self):
        response = self.client.post(
            reverse("category-list"),
            {"company": str(self.company.id), "name": "   "},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("name", response.data)

    def test_create_allows_duplicate_name_in_different_company(self):
        response = self.client.post(
            reverse("category-list"),
            {"company": str(self.other_company.id), "name": self.category.name},
            format="json",
        )

        self.assertEqual(response.status_code, 201)

    def test_create_rejects_parent_category_from_different_company(self):
        parent_category = Category.objects.create(company=self.other_company, name="Other Category")

        response = self.client.post(
            reverse("category-list"),
            {"company": str(self.company.id), "name": "Child Category", "parent_category": str(parent_category.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("parent_category", response.data)

    def test_update_rejects_duplicate_name_in_same_company(self):
        other_category = Category.objects.create(company=self.company, name="Other Category")

        response = self.client.patch(
            reverse("category-detail", args=[self.category.id]),
            {"name": other_category.name},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("name", response.data)

    def test_update_allows_same_name_on_same_category(self):
        response = self.client.patch(
            reverse("category-detail", args=[self.category.id]),
            {"name": self.category.name},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

    def test_update_rejects_blank_name(self):
        response = self.client.patch(
            reverse("category-detail", args=[self.category.id]),
            {"name": "   "},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("name", response.data)

    def test_update_rejects_parent_category_from_different_company(self):
        parent_category = Category.objects.create(company=self.other_company, name="Other Category")

        response = self.client.patch(
            reverse("category-detail", args=[self.category.id]),
            {"parent_category": str(parent_category.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("parent_category", response.data)

    def test_update_rejects_self_parent_category(self):
        response = self.client.patch(
            reverse("category-detail", args=[self.category.id]),
            {"parent_category": str(self.category.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("parent_category", response.data)

    def test_update_rejects_descendant_parent_category(self):
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
        Category.objects.create(company=self.company, name="Child Category", parent_category=self.category)

        response = self.client.patch(
            reverse("category-detail", args=[self.category.id]),
            {"company": str(self.other_company.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("company", response.data)
