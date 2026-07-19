from datetime import datetime
from unittest.mock import Mock

from django.db import IntegrityError
from rest_framework import status
from rest_framework.exceptions import ValidationError as RestValidationError
from rest_framework.test import APITestCase

from api.models import Category, Company
from api.views.category import CategoryViewSet


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
            ({"company": str(self.company.id), "name": "Invalid\x00Name"}, "name"),
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

    def test_unique_constraint_race_is_converted_to_a_validation_error(self):
        database_error = IntegrityError()
        cause = Exception()
        cause.diag = type("Diagnostic", (), {"constraint_name": "unique_company_category_combination"})()
        database_error.__cause__ = cause
        serializer = Mock()
        serializer.save.side_effect = database_error

        with self.assertRaises(RestValidationError):
            CategoryViewSet._save_serializer(serializer)

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

    def test_retrieve_response_has_the_documented_json_shape(self):
        response = self.client.get(f"/api/categories/{self.category.id}/")
        payload = response.json()

        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(payload["id"], str(self.category.id))
        self.assertEqual(payload["company"], str(self.company.id))
        self.assertEqual(payload["parent_category"], str(self.parent.id))
        datetime.fromisoformat(payload["created_at"].replace("Z", "+00:00"))
        datetime.fromisoformat(payload["updated_at"].replace("Z", "+00:00"))
