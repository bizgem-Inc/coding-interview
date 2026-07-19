from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Category, Company


class CategoryValidationTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Example Inc.")
        self.other_company = Company.objects.create(name="Other Inc.")
        self.parent = Category.objects.create(company=self.company, name="Parent")
        self.category = Category.objects.create(company=self.company, name="Engineering", parent_category=self.parent)

    def test_create_rejects_missing_or_invalid_required_values(self):
        cases = [
            ({"name": "Product"}, "company"),
            ({"company": str(self.company.id)}, "name"),
            ({"company": str(self.company.id), "name": ""}, "name"),
            ({"company": str(self.company.id), "name": "x" * 256}, "name"),
            ({"company": "00000000-0000-0000-0000-000000000000", "name": "Product"}, "company"),
            ({"company": str(self.company.id), "name": "Product", "parent_category": "00000000-0000-0000-0000-000000000000"}, "parent_category"),
        ]

        for payload, field in cases:
            with self.subTest(payload=payload):
                response = self.client.post("/api/categories/", payload, format="json")
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(field, response.data)

    def test_create_rejects_malformed_json(self):
        response = self.client.post("/api/categories/", '{"name":', content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_rejects_a_parent_from_another_company(self):
        foreign_parent = Category.objects.create(company=self.other_company, name="Foreign Parent")

        response = self.client.post(
            "/api/categories/",
            {"company": str(self.company.id), "name": "Product", "parent_category": str(foreign_parent.id)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)

    def test_put_requires_all_writable_fields_and_replaces_the_resource(self):
        incomplete_response = self.client.put(
            f"/api/categories/{self.category.id}/",
            {"name": "Platform"},
            format="json",
        )
        complete_response = self.client.put(
            f"/api/categories/{self.category.id}/",
            {"company": str(self.company.id), "name": "Platform", "parent_category": None},
            format="json",
        )

        self.assertEqual(incomplete_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("company", incomplete_response.data)
        self.assertEqual(complete_response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Platform")
        self.assertIsNone(self.category.parent_category)

    def test_patch_rejects_duplicate_name_within_a_company(self):
        Category.objects.create(company=self.company, name="Product")

        response = self.client.patch(
            f"/api/categories/{self.category.id}/",
            {"name": "Product"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_patch_rejects_self_and_cyclic_parent_references(self):
        child = Category.objects.create(company=self.company, name="Child", parent_category=self.category)

        self_response = self.client.patch(
            f"/api/categories/{self.category.id}/",
            {"parent_category": str(self.category.id)},
            format="json",
        )
        cycle_response = self.client.patch(
            f"/api/categories/{self.parent.id}/",
            {"parent_category": str(child.id)},
            format="json",
        )

        self.assertEqual(self_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", self_response.data)
        self.assertEqual(cycle_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", cycle_response.data)

    def test_missing_resources_return_not_found(self):
        unknown_id = "00000000-0000-0000-0000-000000000000"

        self.assertEqual(self.client.get(f"/api/categories/{unknown_id}/").status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.delete(f"/api/categories/{unknown_id}/").status_code, status.HTTP_404_NOT_FOUND)

    def test_deleting_a_company_deletes_its_categories(self):
        category_id = self.category.id

        self.company.delete()

        self.assertFalse(Category.objects.filter(id=category_id).exists())
