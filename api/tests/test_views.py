import uuid

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Category, Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company_a = Company.objects.create(name="Company A")
        self.company_b = Company.objects.create(name="Company B")
        self.category_a = Category.objects.create(
            company=self.company_a,
            name="Category A",
            parent_category=None,
        )

    def test_list(self):
        url = reverse("category-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(self.category_a.id))
        self.assertEqual(response.data[0]["name"], "Category A")
        self.assertIsNone(response.data[0]["parent_category"])

    def test_retrieve(self):
        url = reverse("category-detail", kwargs={"pk": self.category_a.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.category_a.id))
        self.assertEqual(response.data["name"], "Category A")

    def test_create_success(self):
        url = reverse("category-list")
        payload = {
            "company": str(self.company_a.pk),
            "name": "New Category",
            "parent_category": None,
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "New Category")
        self.assertTrue(
            Category.objects.filter(name="New Category", company=self.company_a).exists()
        )

    def test_create_missing_company(self):
        url = reverse("category-list")
        response = self.client.post(url, {"name": "X"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("company", response.data)

    def test_create_missing_name(self):
        url = reverse("category-list")
        response = self.client.post(
            url,
            {"company": str(self.company_a.pk)},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_create_blank_name(self):
        url = reverse("category-list")
        response = self.client.post(
            url,
            {"company": str(self.company_a.pk), "name": "   "},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_put(self):
        url = reverse("category-detail", kwargs={"pk": self.category_a.pk})
        payload = {
            "company": str(self.company_a.pk),
            "name": "Renamed",
            "parent_category": None,
        }
        response = self.client.put(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category_a.refresh_from_db()
        self.assertEqual(self.category_a.name, "Renamed")

    def test_update_patch(self):
        url = reverse("category-detail", kwargs={"pk": self.category_a.pk})
        response = self.client.patch(url, {"name": "Patched"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category_a.refresh_from_db()
        self.assertEqual(self.category_a.name, "Patched")

    def test_destroy(self):
        cat = Category.objects.create(
            company=self.company_a,
            name="To Delete",
            parent_category=None,
        )
        url = reverse("category-detail", kwargs={"pk": cat.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(pk=cat.pk).exists())
        get_response = self.client.get(url)
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_duplicate_company_and_name(self):
        url = reverse("category-list")
        response = self.client.post(
            url,
            {
                "company": str(self.company_a.pk),
                "name": "Category A",
                "parent_category": None,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_parent_from_other_company(self):
        cat_b = Category.objects.create(
            company=self.company_b,
            name="B Only",
            parent_category=None,
        )
        url = reverse("category-list")
        response = self.client.post(
            url,
            {
                "company": str(self.company_a.pk),
                "name": "Should Fail",
                "parent_category": str(cat_b.pk),
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)

    def test_update_self_as_parent(self):
        url = reverse("category-detail", kwargs={"pk": self.category_a.pk})
        response = self.client.patch(
            url,
            {"parent_category": str(self.category_a.pk)},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)

    def test_invalid_company_id(self):
        url = reverse("category-list")
        fake_id = str(uuid.uuid4())
        response = self.client.post(
            url,
            {"company": fake_id, "name": "X", "parent_category": None},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_parent_category_id(self):
        url = reverse("category-list")
        fake_id = str(uuid.uuid4())
        response = self.client.post(
            url,
            {
                "company": str(self.company_a.pk),
                "name": "Orphan",
                "parent_category": fake_id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_set_descendant_as_parent(self):
        child = Category.objects.create(
            company=self.company_a,
            name="Child",
            parent_category=self.category_a,
        )
        grandchild = Category.objects.create(
            company=self.company_a,
            name="Grandchild",
            parent_category=child,
        )
        url = reverse("category-detail", kwargs={"pk": self.category_a.pk})
        response = self.client.patch(
            url,
            {"parent_category": str(grandchild.pk)},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)
