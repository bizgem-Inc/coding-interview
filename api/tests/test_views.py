import uuid

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        """Set up test data."""
        # Create test companies
        self.company1 = Company.objects.create(name="Test Company 1")
        self.company2 = Company.objects.create(name="Test Company 2")
        
        # Create test categories
        self.category1 = Category.objects.create(
            company=self.company1,
            name="Category 1",
            parent_category=None
        )
        self.category2 = Category.objects.create(
            company=self.company1,
            name="Category 2",
            parent_category=None
        )
        self.category3 = Category.objects.create(
            company=self.company1,
            name="Subcategory 1",
            parent_category=self.category1
        )
        self.category4 = Category.objects.create(
            company=self.company2,
            name="Category 1"
        )

    def test_list(self):
        """Test listing all categories."""
        url = reverse("category-list")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
        
        # Check that all categories are returned
        category_names = [cat["name"] for cat in response.data]
        self.assertIn("Category 1", category_names)
        self.assertIn("Category 2", category_names)
        self.assertIn("Subcategory 1", category_names)

    def test_retrieve(self):
        """Test retrieving a specific category."""
        url = reverse("category-detail", kwargs={"pk": self.category1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.category1.id))
        self.assertEqual(response.data["name"], "Category 1")
        self.assertEqual(response.data["company"], str(self.company1.id))
        self.assertIsNone(response.data["parent_category"])

    def test_retrieve_with_parent(self):
        """Test retrieving a category with a parent category."""
        url = reverse("category-detail", kwargs={"pk": self.category3.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Subcategory 1")
        self.assertEqual(response.data["parent_category"], str(self.category1.id))

    def test_retrieve_not_found(self):
        """Test retrieving a non-existent category."""
        fake_id = uuid.uuid4()
        url = reverse("category-detail", kwargs={"pk": fake_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create(self):
        """Test creating a new category."""
        url = reverse("category-list")
        data = {
            "company": str(self.company1.id),
            "name": "New Category"
        }
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "New Category")
        self.assertEqual(response.data["company"], str(self.company1.id))
        self.assertIsNone(response.data["parent_category"])
        
        # Verify the category was created in the database
        self.assertTrue(Category.objects.filter(name="New Category").exists())

    def test_create_with_parent(self):
        """Test creating a category with a parent category."""
        url = reverse("category-list")
        data = {
            "company": str(self.company1.id),
            "name": "New Subcategory",
            "parent_category": str(self.category1.id)
        }
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "New Subcategory")
        self.assertEqual(response.data["parent_category"], str(self.category1.id))

    def test_create_duplicate_name_same_company(self):
        """Test that creating a category with duplicate name in same company fails."""
        url = reverse("category-list")
        data = {
            "company": str(self.company1.id),
            "name": "Category 1"  # Already exists for company1
        }
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_create_duplicate_name_different_company(self):
        """Test that creating a category with duplicate name in different company succeeds."""
        url = reverse("category-list")
        data = {
            "company": str(self.company2.id),
            "name": "Category 1"  # Exists for company1, but not company2
        }
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_parent_different_company(self):
        """Test that creating a category with parent from different company fails."""
        url = reverse("category-list")
        data = {
            "company": str(self.company2.id),
            "name": "New Category",
            "parent_category": str(self.category1.id)  # category1 belongs to company1
        }
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)

    def test_create_invalid_company(self):
        """Test creating a category with invalid company ID."""
        url = reverse("category-list")
        fake_company_id = uuid.uuid4()
        data = {
            "company": str(fake_company_id),
            "name": "New Category"
        }
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_missing_required_fields(self):
        """Test creating a category without required fields."""
        url = reverse("category-list")
        data = {}  # Missing company and name
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("company", response.data)
        self.assertIn("name", response.data)

    def test_update(self):
        """Test full update of a category."""
        url = reverse("category-detail", kwargs={"pk": self.category1.id})
        data = {
            "company": str(self.company1.id),
            "name": "Updated Category 1"
        }
        response = self.client.put(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Category 1")
        
        # Verify the update in the database
        self.category1.refresh_from_db()
        self.assertEqual(self.category1.name, "Updated Category 1")

    def test_partial_update(self):
        """Test partial update of a category."""
        url = reverse("category-detail", kwargs={"pk": self.category1.id})
        data = {
            "name": "Partially Updated Category"
        }
        response = self.client.patch(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Partially Updated Category")
        # Company should remain unchanged
        self.assertEqual(response.data["company"], str(self.company1.id))

    def test_update_parent_category(self):
        """Test updating a category's parent."""
        url = reverse("category-detail", kwargs={"pk": self.category3.id})
        data = {
            "company": str(self.company1.id),
            "name": "Subcategory 1",
            "parent_category": str(self.category2.id)
        }
        response = self.client.put(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["parent_category"], str(self.category2.id))

    def test_update_remove_parent(self):
        """Test removing a parent category from a category."""
        url = reverse("category-detail", kwargs={"pk": self.category3.id})
        data = {
            "company": str(self.company1.id),
            "name": "Subcategory 1",
            "parent_category": None
        }
        response = self.client.put(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data["parent_category"])

    def test_update_duplicate_name(self):
        """Test that updating to duplicate name in same company fails."""
        url = reverse("category-detail", kwargs={"pk": self.category2.id})
        data = {
            "company": str(self.company1.id),
            "name": "Category 1"  # Already exists for category1
        }
        response = self.client.put(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_update_not_found(self):
        """Test updating a non-existent category."""
        fake_id = uuid.uuid4()
        url = reverse("category-detail", kwargs={"pk": fake_id})
        data = {
            "company": str(self.company1.id),
            "name": "Updated Name"
        }
        response = self.client.put(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_destroy(self):
        """Test deleting a category."""
        category_id = self.category2.id
        url = reverse("category-detail", kwargs={"pk": category_id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify the category was deleted
        self.assertFalse(Category.objects.filter(id=category_id).exists())

    def test_destroy_not_found(self):
        """Test deleting a non-existent category."""
        fake_id = uuid.uuid4()
        url = reverse("category-detail", kwargs={"pk": fake_id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_destroy_with_children(self):
        """Test that deleting a category with children sets parent_category to NULL."""
        # category1 has category3 as a child
        category1_id = self.category1.id
        category3_id = self.category3.id
        
        url = reverse("category-detail", kwargs={"pk": category1_id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify category1 was deleted
        self.assertFalse(Category.objects.filter(id=category1_id).exists())
        
        # Verify category3's parent_category is now NULL
        self.category3.refresh_from_db()
        self.assertIsNone(self.category3.parent_category)
