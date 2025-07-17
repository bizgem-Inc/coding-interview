import uuid

from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Category, Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        # Dummy Data
        company0 = Company.objects.create(name="com0")

        self.category0 = Category.objects.create(company=company0, name="cat0", parent_category=None)
        self.category0_1 = Category.objects.create(company=company0, name="cat0_1", parent_category=self.category0)
        self.category1 = Category.objects.create(company=company0, name="cat1", parent_category=None)

        self.companies = [company0]
        self.categories = [self.category0, self.category0_1, self.category1]

        # URL (Intentionally hardcoded)
        self.list_url = "/api/categories/"
        self.create_url = "/api/categories/"

    def test_list_no_date(self):
        """
        The response should be an empty list if no categoy is.
        """

        Category.objects.all().delete()

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 0)

    def test_list(self):
        """
        The response should include all the categories
        """

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), len(self.categories))

        ids_in_db = [str(cat.id) for cat in self.categories]
        for cat in response.data:
            self.assertIn(cat["id"], ids_in_db)

    @staticmethod
    def __retrieve_url(pk):
        return f"/api/categories/{pk}/"

    def test_retrieve(self):
        """
        It should be able to retrieve all the element in DB.
        """

        for cat in self.categories:
            url = self.__retrieve_url(cat.id)
            response = self.client.get(url)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["id"], str(cat.id))

    def test_retrieve_non_existent_category(self):
        """
        It should return 404 Error to retrieve non existent category.
        """

        pk = uuid.uuid4()
        url = self.__retrieve_url(pk)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create(self):
        """
        It should create both root category and leaf category.
        """

        ##
        # Try to create a root category (without parent_category)
        ##
        data0 = {
            "name": "cat100",
            "company": str(self.companies[0].id),
        }

        response0 = self.client.post(self.create_url, data0, format="json")

        # Check the response0
        self.assertEqual(response0.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response0.data)
        self.assertEqual(response0.data["name"], data0["name"])
        self.assertEqual(str(response0.data["company"]), data0["company"])
        self.assertIsNone(response0.data["parent_category"])

        # Check the DB
        self.assertEqual(Category.objects.count(), len(self.categories) + 1)
        ids_in_db = [str(cat.id) for cat in Category.objects.all()]
        self.assertIn(response0.data["id"], ids_in_db)

        cat_in_db = Category.objects.get(pk=uuid.UUID(response0.data["id"]))
        self.assertEqual(cat_in_db.name, data0["name"])
        self.assertEqual(str(cat_in_db.company.id), data0["company"])
        self.assertIsNone(cat_in_db.parent_category)

        ##
        # Try to create a leaf category
        ##
        data1 = {"name": "cat100_1", "company": str(self.companies[0].id), "parent_category": str(response0.data["id"])}

        response1 = self.client.post(self.create_url, data1, format="json")

        # Check the response1
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response1.data)
        self.assertEqual(response1.data["name"], data1["name"])
        self.assertEqual(str(response1.data["company"]), data1["company"])
        self.assertEqual(str(response1.data["parent_category"]), data1["parent_category"])

        # Check the DB
        self.assertEqual(Category.objects.count(), len(self.categories) + 2)
        ids_in_db = [str(cat.id) for cat in Category.objects.all()]
        self.assertIn(response1.data["id"], ids_in_db)

        cat_in_db = Category.objects.get(pk=uuid.UUID(response1.data["id"]))
        self.assertEqual(cat_in_db.name, data1["name"])
        self.assertEqual(str(cat_in_db.company.id), data1["company"])
        self.assertEqual(str(cat_in_db.parent_category.id), data1["parent_category"])

    def test_create_non_exist_company(self):
        """
        It should return an error if the company does not exist.
        """

        ##
        # Try to create a root category (without parent_category)
        ##
        data0 = {
            "name": "cat100",
            "company": str(uuid.uuid4()),
        }

        response0 = self.client.post(self.create_url, data0, format="json")

        # Check the response0
        self.assertEqual(response0.status_code, status.HTTP_400_BAD_REQUEST)

        # Check the DB
        self.assertEqual(Category.objects.count(), len(self.categories))

        ##
        # Try to create a leaf category
        ##
        data1 = {"name": "cat100", "company": str(uuid.uuid4()), "parent_category": str(self.categories[0].id)}

        response1 = self.client.post(self.create_url, data1, format="json")

        # Check the response0
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)

        # Check the DB
        self.assertEqual(Category.objects.count(), len(self.categories))

    def test_create_non_exist_parent_category(self):
        """
        It should return an error if the parent_category does not exist.
        """

        data = {
            "name": "cat100",
            "company": str(self.companies[0].id),
            "parent_category": str(uuid.uuid4()),
        }

        response = self.client.post(self.create_url, data, format="json")

        # Check the response0
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check the DB
        self.assertEqual(Category.objects.count(), len(self.categories))

    def test_create_with_different_company(self):
        """
        How should it behave if the company is different from that of the parent_category?
        """

        pass

    @staticmethod
    def __update_url(pk):
        return f"/api/categories/{pk}/"

    def test_update_name(self):
        """
        It should change the name.
        """

        for cat in self.categories:
            data = {"name": f"new_{cat.name}"}

            response = self.client.patch(self.__update_url(cat.id), data, format="json")

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["id"], str(cat.id))
            self.assertEqual(response.data["name"], data["name"])

            if cat.parent_category is None:
                self.assertIsNone(response.data["parent_category"])
            else:
                self.assertEqual(response.data["parent_category"], cat.parent_category.id)

    def test_update_parent_category(self):
        """
        How should it behave to update the parent_category?
        """

        pass

    def test_update_post(self):
        """
        How should it behave to updat all?
        """

        pass

    @staticmethod
    def __destroy_url(pk):
        return f"/api/categories/{pk}/"

    def test_destroy(self):
        pass

    def test_destroy_leaf(self):
        """
        It should delete only the specified category if it is a leaf.
        """

        cat = self.category0_1

        response = self.client.delete(self.__destroy_url(cat.id))

        # Check the response
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data, None)

        # Check the DB
        self.assertEqual(Category.objects.count(), len(self.categories) - 1)
        with self.assertRaises(Category.DoesNotExist):
            Category.objects.get(pk=cat.id)

    def test_destroy_root(self):
        """
        It should delete only the specified category and the children will be root.
        """

        cat = self.category0
        response = self.client.delete(self.__destroy_url(cat.id))

        # Check the response
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data, None)

        # Check the DB
        self.assertEqual(Category.objects.count(), len(self.categories) - 1)
        with self.assertRaises(Category.DoesNotExist):
            Category.objects.get(pk=cat.id)

        # Check the child
        child = Category.objects.get(pk=self.category0_1.id)
        self.assertIsNone(child.parent_category)

    def test_destroy_non_exist_category(self):
        """
        It should cause an error if the specified category does not exist.
        """

        pk = uuid.uuid4()
        response = self.client.delete(self.__destroy_url(pk))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Category.objects.count(), len(self.categories))
