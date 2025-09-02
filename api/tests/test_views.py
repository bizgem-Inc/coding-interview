from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from api.models.company import Company
from api.models.category import Category


class CategoryViewTests(APITestCase):
    def setUp(self):
        # Create Demo Company
        self.company = Company.objects.create(name="Demo Company")
        self.list_url = reverse("category-list")

    def _create_category(self, name="Books", parent_id=None):
        payload = {"company": str(self.company.id), "name": name}
        if parent_id:
            payload["parent_category"] = str(parent_id)
        r = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED, r.data)
        return r.data  # {id, name, ...}

    # Happy path
    def test_list(self):
        self._create_category("Books")
        self._create_category("Novels")
        r = self.client.get(self.list_url)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        names = {x["name"] for x in r.data}
        self.assertTrue({"Books", "Novels"}.issubset(names))

    def test_retrieve(self):
        c = self._create_category("Books")
        r = self.client.get(reverse("category-detail", args=[c["id"]]))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data["id"], c["id"])

    def test_create(self):
        c = self._create_category("Books")
        self.assertEqual(c["name"], "Books")

    def test_update(self):
        c = self._create_category("Books")
        r = self.client.patch(
            reverse("category-detail", args=[c["id"]]),
            {"name": "Novels"},
            format="json",
        )
        self.assertIn(r.status_code, (status.HTTP_200_OK, status.HTTP_204_NO_CONTENT))
        r2 = self.client.get(reverse("category-detail", args=[c["id"]]))
        self.assertEqual(r2.status_code, status.HTTP_200_OK)
        self.assertEqual(r2.data["name"], "Novels")

    def test_destroy(self):
        c = self._create_category("Books")
        r = self.client.delete(reverse("category-detail", args=[c["id"]]))
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
        r2 = self.client.get(reverse("category-detail", args=[c["id"]]))
        self.assertEqual(r2.status_code, status.HTTP_404_NOT_FOUND)

    # Failure case
    def test_create_requires_name(self):
        """missing name -> 400"""
        r = self.client.post(
            self.list_url,
            {"company": str(self.company.id)},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", r.data)

    def test_parent_company_must_match(self):
        """parent category must belong to the same company"""
        other = Company.objects.create(name="Other Co")
        parent_other = Category.objects.create(company=other, name="OtherParent")
        r = self.client.post(
            self.list_url,
            {
                "company": str(self.company.id),
                "name": "Child",
                "parent_category": str(parent_other.id),
            },
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", r.data)

    def test_cannot_set_self_as_parent(self):
        """cannot set itself as parent (PATCH)"""
        c = self._create_category("Self")
        r = self.client.patch(
            reverse("category-detail", args=[c["id"]]),
            {"parent_category": c["id"]},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", r.data)

    def test_cannot_create_cycle(self):
        """disallow cycles: after child -> parent, setting parent -> child must return 400"""
        p = self._create_category("Parent")
        c = self._create_category("Child", parent_id=p["id"])
        r = self.client.patch(
            reverse("category-detail", args=[p["id"]]),
            {"parent_category": c["id"]},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", r.data)

    def test_unique_name_within_company(self):
        """name must be unique within the same company"""
        self._create_category("Books")
        r = self.client.post(
            self.list_url,
            {"company": str(self.company.id), "name": "Books"},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        # Accept either field-level ("name") or serializer-level ("non_field_errors")
        self.assertTrue(("name" in r.data) or ("non_field_errors" in r.data), r.data)
