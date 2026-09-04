from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Category, Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="テスト企業")
        self.other_company = Company.objects.create(name="別企業")
        self.parent = Category.objects.create(company=self.company, name="食品")
        self.child = Category.objects.create(company=self.company, name="菓子", parent_category=self.parent)
        self.other_category = Category.objects.create(company=self.other_company, name="食品")

    def detail_url(self, category):
        return reverse("category-detail", kwargs={"pk": category.pk})

    # ---- list ----

    def test_list(self):
        response = self.client.get(reverse("category-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [item["id"] for item in response.json()],
            [str(self.parent.id), str(self.child.id), str(self.other_category.id)],
        )

    def test_list_filtered_by_company(self):
        response = self.client.get(reverse("category-list"), {"company": self.other_company.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["id"] for item in response.json()], [str(self.other_category.id)])

    def test_list_rejects_malformed_company_filter(self):
        response = self.client.get(reverse("category-list"), {"company": "not-a-uuid"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("company", response.json())

    # ---- retrieve ----

    def test_retrieve(self):
        response = self.client.get(self.detail_url(self.child))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        self.assertEqual(body["id"], str(self.child.id))
        self.assertEqual(body["company"], str(self.company.id))
        self.assertEqual(body["name"], "菓子")
        self.assertEqual(body["parent_category"], str(self.parent.id))
        self.assertIn("created_at", body)
        self.assertIn("updated_at", body)

    def test_retrieve_not_found(self):
        response = self.client.get(reverse("category-detail", kwargs={"pk": "00000000-0000-0000-0000-000000000000"}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ---- create ----

    def test_create(self):
        payload = {"company": self.company.id, "name": "飲料", "parent_category": self.parent.id}

        response = self.client.post(reverse("category-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Category.objects.get(id=response.json()["id"])
        self.assertEqual(created.company, self.company)
        self.assertEqual(created.name, "飲料")
        self.assertEqual(created.parent_category, self.parent)

    def test_create_without_parent(self):
        response = self.client.post(reverse("category-list"), {"company": self.company.id, "name": "日用品"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.json()["parent_category"])

    def test_create_requires_company_and_name(self):
        response = self.client.post(reverse("category-list"), {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(set(response.json()), {"company", "name"})

    def test_create_rejects_malformed_company(self):
        response = self.client.post(reverse("category-list"), {"company": "not-a-uuid", "name": "飲料"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("company", response.json())

    def test_create_rejects_nonexistent_company(self):
        payload = {"company": "00000000-0000-0000-0000-000000000000", "name": "飲料"}

        response = self.client.post(reverse("category-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("company", response.json())

    def test_create_rejects_blank_name(self):
        response = self.client.post(reverse("category-list"), {"company": self.company.id, "name": ""}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.json())

    def test_create_name_length_boundary(self):
        url = reverse("category-list")

        accepted = self.client.post(url, {"company": self.company.id, "name": "a" * 255}, format="json")
        rejected = self.client.post(url, {"company": self.company.id, "name": "b" * 256}, format="json")

        self.assertEqual(accepted.status_code, status.HTTP_201_CREATED)
        self.assertEqual(rejected.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", rejected.json())

    def test_create_rejects_duplicate_name_within_company(self):
        response = self.client.post(reverse("category-list"), {"company": self.company.id, "name": "食品"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.json())
        self.assertEqual(Category.objects.filter(company=self.company, name="食品").count(), 1)

    def test_create_allows_same_name_in_other_company(self):
        response = self.client.post(reverse("category-list"), {"company": self.other_company.id, "name": "菓子"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_rejects_parent_of_other_company(self):
        payload = {"company": self.company.id, "name": "飲料", "parent_category": self.other_category.id}

        response = self.client.post(reverse("category-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.json())

    # ---- update ----

    def test_update(self):
        payload = {"company": self.company.id, "name": "スナック", "parent_category": None}

        response = self.client.put(self.detail_url(self.child), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.child.refresh_from_db()
        self.assertEqual(self.child.name, "スナック")
        self.assertIsNone(self.child.parent_category)

    def test_partial_update(self):
        response = self.client.patch(self.detail_url(self.child), {"name": "スナック"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.child.refresh_from_db()
        self.assertEqual(self.child.name, "スナック")
        self.assertEqual(self.child.parent_category, self.parent)

    def test_update_rejects_duplicate_name_within_company(self):
        response = self.client.patch(self.detail_url(self.child), {"name": "食品"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.json())

    def test_update_rejects_self_as_parent(self):
        response = self.client.patch(self.detail_url(self.parent), {"parent_category": self.parent.id}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.json())

    def test_update_rejects_descendant_as_parent(self):
        grandchild = Category.objects.create(company=self.company, name="チョコレート", parent_category=self.child)

        response = self.client.patch(self.detail_url(self.parent), {"parent_category": grandchild.id}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.json())

    def test_update_rejects_moving_to_company_of_parent_mismatch(self):
        # 親を持ったまま別企業へ移すと、親が別企業のカテゴリになるため拒否される
        response = self.client.patch(self.detail_url(self.child), {"company": self.other_company.id}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.json())

    # ---- destroy ----

    def test_destroy(self):
        response = self.client.delete(self.detail_url(self.child))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.child.id).exists())

    def test_destroy_parent_detaches_children(self):
        response = self.client.delete(self.detail_url(self.parent))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.child.refresh_from_db()
        self.assertIsNone(self.child.parent_category)

    def test_destroy_not_found(self):
        response = self.client.delete(reverse("category-detail", kwargs={"pk": "00000000-0000-0000-0000-000000000000"}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
