from rest_framework import status
from rest_framework.test import APITestCase

from django.urls import reverse

from api.models.category import Category
from api.models.company import Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Acme")
        self.category = Category.objects.create(company=self.company, name="Tools")

    def test_list(self):
        Category.objects.create(company=self.company, name="Hardware")

        response = self.client.get(reverse("category-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve(self):
        response = self.client.get(reverse("category-detail", args=[self.category.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Tools")

    def test_retrieve_not_found(self):
        response = self.client.get(
            reverse("category-detail", args=["00000000-0000-0000-0000-000000000000"])
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create(self):
        payload = {"company": str(self.company.id), "name": "Software"}

        response = self.client.post(reverse("category-list"), payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)
        self.assertTrue(
            Category.objects.filter(company=self.company, name="Software").exists()
        )

    def test_create_with_parent_category(self):
        payload = {
            "company": str(self.company.id),
            "name": "Power Tools",
            "parent_category": str(self.category.id),
        }

        response = self.client.post(reverse("category-list"), payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Category.objects.get(name="Power Tools")
        self.assertEqual(created.parent_category_id, self.category.id)

    def test_create_missing_required_field(self):
        response = self.client.post(reverse("category-list"), {"company": str(self.company.id)})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_create_name_too_long(self):
        payload = {"company": str(self.company.id), "name": "a" * 256}

        response = self.client.post(reverse("category-list"), payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(Category.objects.count(), 1)

    def test_create_name_max_length(self):
        payload = {"company": str(self.company.id), "name": "a" * 255}

        response = self.client.post(reverse("category-list"), payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(name="a" * 255).exists())

    def test_create_duplicate_company_name_combination(self):
        payload = {"company": str(self.company.id), "name": "Tools"}

        response = self.client.post(reverse("category-list"), payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Category.objects.count(), 1)

    def test_update(self):
        payload = {"company": str(self.company.id), "name": "Renamed"}

        response = self.client.put(
            reverse("category-detail", args=[self.category.id]), payload
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Renamed")

    def test_partial_update(self):
        response = self.client.patch(
            reverse("category-detail", args=[self.category.id]), {"name": "Patched"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Patched")

    def test_destroy(self):
        response = self.client.delete(
            reverse("category-detail", args=[self.category.id])
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())
