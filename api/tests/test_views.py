from rest_framework import status
from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Company A")
        self.other_company = Company.objects.create(name="Company B")
        self.category = Category.objects.create(company=self.company, name="Category A")

    def test_list(self):
        Category.objects.create(company=self.other_company, name="Category B")

        response = self.client.get("/api/categories/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve(self):
        response = self.client.get(f"/api/categories/{self.category.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.category.id))
        self.assertEqual(response.data["name"], self.category.name)

    def test_retrieve_not_found(self):
        response = self.client.get("/api/categories/11111111-1111-1111-1111-111111111111/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create(self):
        payload = {"company": str(self.company.id), "name": "New Category"}

        response = self.client.post("/api/categories/", payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(company=self.company, name="New Category").exists())

    def test_create_with_parent_category(self):
        payload = {
            "company": str(self.company.id),
            "name": "Child Category",
            "parent_category": str(self.category.id),
        }

        response = self.client.post("/api/categories/", payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Category.objects.get(id=response.data["id"])
        self.assertEqual(created.parent_category, self.category)

    def test_create_missing_name(self):
        payload = {"company": str(self.company.id)}

        response = self.client.post("/api/categories/", payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_create_missing_company(self):
        payload = {"name": "No Company"}

        response = self.client.post("/api/categories/", payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("company", response.data)

    def test_create_duplicate_name_in_same_company(self):
        payload = {"company": str(self.company.id), "name": self.category.name}

        response = self.client.post("/api/categories/", payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_same_name_different_company_is_allowed(self):
        payload = {"company": str(self.other_company.id), "name": self.category.name}

        response = self.client.post("/api/categories/", payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_parent_category_from_different_company_is_rejected(self):
        other_category = Category.objects.create(company=self.other_company, name="Category B")
        payload = {
            "company": str(self.company.id),
            "name": "Child Category",
            "parent_category": str(other_category.id),
        }

        response = self.client.post("/api/categories/", payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)

    def test_update(self):
        payload = {"company": str(self.company.id), "name": "Updated Name"}

        response = self.client.put(f"/api/categories/{self.category.id}/", payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Updated Name")

    def test_partial_update(self):
        response = self.client.patch(f"/api/categories/{self.category.id}/", {"name": "Patched Name"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Patched Name")

    def test_update_self_parent_is_rejected(self):
        payload = {
            "company": str(self.company.id),
            "name": self.category.name,
            "parent_category": str(self.category.id),
        }

        response = self.client.put(f"/api/categories/{self.category.id}/", payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)

    def test_update_descendant_as_parent_is_rejected(self):
        child = Category.objects.create(company=self.company, name="Child", parent_category=self.category)

        response = self.client.patch(f"/api/categories/{self.category.id}/", {"parent_category": str(child.id)})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)

    def test_destroy(self):
        response = self.client.delete(f"/api/categories/{self.category.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())

    def test_destroy_sets_children_parent_to_null(self):
        child = Category.objects.create(company=self.company, name="Child", parent_category=self.category)

        response = self.client.delete(f"/api/categories/{self.category.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        child.refresh_from_db()
        self.assertIsNone(child.parent_category)
