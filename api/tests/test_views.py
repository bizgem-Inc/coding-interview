from rest_framework.test import APITestCase
from rest_framework import status
from api.models.category import Category
from api.models.company import Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        # Create a company
        self.company = Company.objects.create(name="test_company")

        # Create a category
        self.category = Category.objects.create(name="food", company=self.company)

    # test for GET to "/api/categories/"
    # success
    def test_list(self):
        response = self.client.get("/api/categories/")
        # check if the HTTP status code is 200(ok)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # get all categories as list
        names = [item["name"] for item in response.data]
        self.assertIn("food", names)

    # test for GET to "/categories/<id>"
    # success
    def test_retrieve(self):
        url = f"/api/categories/{self.category.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "food")

    # failure for not existing id
    def test_retrieve_not_found(self):
        url = "/api/categories/9999999999/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # test for POST to "/api/categories/"
    # success
    def test_create(self):
        data = {
            "name": "food",
            "company": str(self.company.id),  # return uuid as str
        }
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "food")
        self.assertEqual(response.data["company"], str(self.company.id))

    # failure for empty name
    def test_create_empty_name(self):
        data = {"name": "   ", "company": str(self.company.id)}
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("may not be blank", str(response.data))

    # failure for creating duplicate category within same company
    def test_create_duplicate_name(self):
        data = {"name": "food", "company": str(self.company.id)}
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already exists", str(response.data))

    # failure for setting other company's category as its parent category
    def test_create_parent_from_different_company(self):
        self.other_company = Company.objects.create(name="other_company")
        other_category = Category.objects.create(
            name="other_cat", company=self.other_company
        )
        data = {
            "name": "child_cat",
            "company": str(self.company.id),
            "parent_category": str(other_category.id),
        }
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Parent category must belong to the same company", str(response.data)
        )

    # test for PUT to "/api/categories/"
    # success
    def test_update(self):
        data = {
            "name": "updated_food",
            "company": str(self.company.id),
        }
        url = f"/api/categories/{self.category.id}/"
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "updated_food")

    # failure for updating its category to itself
    def test_create_self_as_parent(self):
        data = {
            "name": self.category.name,
            "company": str(self.company.id),
            "parent_category": str(self.category.id),
        }
        url = f"/api/categories/{self.category.id}/"
        # using PUT method coz this situation occurs when the category already exists and try to update its parent category
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("cannot be its own parent", str(response.data))

    # test for DELETE to "/api/categories/<id>"
    # success
    def test_destroy(self):
        url = f"/api/categories/{self.category.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Check that the object is gone
        exists = Category.objects.filter(id=self.category.id).exists()
        self.assertFalse(exists)

    # failure for not existing id
    def test_destroy_not_found(self):
        url = "/api/categories/9999999999/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
