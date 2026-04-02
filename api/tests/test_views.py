from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company


class CategoryViewTests(APITestCase):
    def setUp(self) -> None:
        self.primary_company = Company.objects.create(name="Primary Company")
        self.secondary_company = Company.objects.create(name="Secondary Company")
        self.parent_category = Category.objects.create(
            company=self.primary_company,
            name="Parent Category",
        )
        self.child_category = Category.objects.create(
            company=self.primary_company,
            name="Child Category",
            parent_category=self.parent_category,
        )
        self.secondary_company_category = Category.objects.create(
            company=self.secondary_company,
            name="External Category",
        )

    def test_list(self) -> None:
        """Verify the category list endpoint returns every category."""
        response = self.client.get(reverse("category-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(len(response.data), 3)
        self.assertCountEqual(
            [item["id"] for item in response.data],
            [
                str(self.parent_category.id),
                str(self.child_category.id),
                str(self.secondary_company_category.id),
            ],
        )

    def test_retrieve(self) -> None:
        """Verify the category detail endpoint returns one category."""
        response = self.client.get(
            reverse("category-detail", args=[self.child_category.id])
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data["id"], str(self.child_category.id))
        self.assertEqual(response.data["name"], self.child_category.name)
        self.assertEqual(
            str(response.data["parent_category"]),
            str(self.parent_category.id),
        )

    def test_create(self) -> None:
        """Verify a valid POST request creates a category."""
        payload = {
            "company": str(self.primary_company.id),
            "name": "Accessories",
            "parent_category": str(self.parent_category.id),
        }

        response = self.client.post(reverse("category-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertTrue(
            Category.objects.filter(
                company=self.primary_company,
                name="Accessories",
                parent_category=self.parent_category,
            ).exists()
        )

    def test_create_rejects_duplicate_name_within_company(self) -> None:
        """Verify duplicate category names within one company are rejected."""
        payload = {
            "company": str(self.primary_company.id),
            "name": self.parent_category.name,
            "parent_category": None,
        }

        response = self.client.post(reverse("category-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_create_rejects_parent_category_from_other_company(self) -> None:
        """Verify a parent category from another company is rejected."""
        payload = {
            "company": str(self.primary_company.id),
            "name": "Invalid Parent",
            "parent_category": str(self.secondary_company_category.id),
        }

        response = self.client.post(reverse("category-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)

    def test_update(self) -> None:
        """Verify a PUT request updates an existing category."""
        payload = {
            "company": str(self.primary_company.id),
            "name": "Updated Child Category",
            "parent_category": str(self.parent_category.id),
        }

        response = self.client.put(
            reverse("category-detail", args=[self.child_category.id]),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.child_category.refresh_from_db()
        self.assertEqual(self.child_category.name, "Updated Child Category")

    def test_partial_update(self) -> None:
        """Verify a PATCH request partially updates an existing category."""
        payload = {"name": "Patched Child Category"}

        response = self.client.patch(
            reverse("category-detail", args=[self.child_category.id]),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.child_category.refresh_from_db()
        self.assertEqual(self.child_category.name, "Patched Child Category")

    def test_destroy(self) -> None:
        """Verify a DELETE request removes a category."""
        response = self.client.delete(
            reverse("category-detail", args=[self.child_category.id])
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.child_category.id).exists())
