import uuid

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Category, Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Company")
        self.other_company = Company.objects.create(name="Other company")
        self.category = Category.objects.create(company=self.company, name="Parent")
        self.child = Category.objects.create(company=self.company, name="Child", parent_category=self.category)
        self.list_url = reverse("category-list")
        self.detail_url = reverse("category-detail", args=[self.category.pk])

    def payload(self, **overrides):
        data = {"company": str(self.company.pk), "name": "New category"}
        data.update(overrides)
        return data

    def assert_invalid(self, response, field):
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(field, response.data)

    def test_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["id"] for item in response.data], [str(self.category.pk), str(self.child.pk)])
        self.assertEqual(response.data[1]["parent_category"], self.category.pk)

    def test_list_empty(self):
        Category.objects.all().delete()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_retrieve(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.category.pk))
        self.assertEqual(response.data["company"], self.company.pk)
        self.assertEqual(response.data["name"], "Parent")
        self.assertIsNone(response.data["parent_category"])
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data)

    def test_create(self):
        response = self.client.post(self.list_url, self.payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        category = Category.objects.get(pk=response.data["id"])
        self.assertEqual(category.company, self.company)
        self.assertEqual(category.name, "New category")
        self.assertIsNone(category.parent_category)

    def test_create_with_parent(self):
        response = self.client.post(self.list_url, self.payload(parent_category=str(self.category.pk)), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.get(pk=response.data["id"]).parent_category, self.category)

    def test_create_with_null_parent(self):
        response = self.client.post(self.list_url, self.payload(parent_category=None), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(Category.objects.get(pk=response.data["id"]).parent_category)

    def test_create_invalid_fields(self):
        cases = [
            ({"name": ""}, "name"),
            ({"name": "   "}, "name"),
            ({"name": None}, "name"),
            ({"name": "x" * 256}, "name"),
            ({"company": None}, "company"),
            ({"company": "invalid"}, "company"),
            ({"company": str(uuid.uuid4())}, "company"),
            ({"parent_category": "invalid"}, "parent_category"),
            ({"parent_category": str(uuid.uuid4())}, "parent_category"),
        ]
        for overrides, field in cases:
            with self.subTest(overrides=overrides):
                response = self.client.post(self.list_url, self.payload(**overrides), format="json")
                self.assert_invalid(response, field)
                self.assertEqual(Category.objects.count(), 2)

    def test_create_requires_company_and_name(self):
        for field in ("company", "name"):
            with self.subTest(field=field):
                data = self.payload()
                del data[field]
                self.assert_invalid(self.client.post(self.list_url, data, format="json"), field)
        self.assertEqual(Category.objects.count(), 2)

    def test_create_name_max_length(self):
        response = self.client.post(self.list_url, self.payload(name="x" * 255), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_rejects_duplicate_name_for_company(self):
        response = self.client.post(self.list_url, self.payload(name="Parent"), format="json")
        self.assert_invalid(response, "name")
        self.assertEqual(Category.objects.count(), 2)

    def test_create_allows_same_name_in_other_company(self):
        response = self.client.post(self.list_url, self.payload(company=str(self.other_company.pk), name="Parent"), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_rejects_parent_in_other_company(self):
        response = self.client.post(self.list_url, self.payload(company=str(self.other_company.pk), parent_category=str(self.category.pk)), format="json")
        self.assert_invalid(response, "parent_category")
        self.assertEqual(Category.objects.count(), 2)

    def test_create_ignores_read_only_fields(self):
        supplied_id = uuid.uuid4()
        response = self.client.post(self.list_url, self.payload(id=str(supplied_id), created_at="2000-01-01T00:00:00Z", updated_at="2000-01-01T00:00:00Z"), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        category = Category.objects.get(pk=response.data["id"])
        self.assertNotEqual(category.pk, supplied_id)
        self.assertNotEqual(category.created_at.year, 2000)
        self.assertNotEqual(category.updated_at.year, 2000)

    def test_update(self):
        created_at = self.category.created_at
        updated_at = self.category.updated_at
        response = self.client.put(self.detail_url, self.payload(name="Updated", parent_category=None), format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Updated")
        self.assertEqual(self.category.created_at, created_at)
        self.assertGreater(self.category.updated_at, updated_at)

    def test_partial_update(self):
        response = self.client.patch(self.detail_url, {"name": "Updated"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Updated")
        self.assertEqual(self.category.company, self.company)

    def test_update_unchanged_name(self):
        response = self.client.put(self.detail_url, self.payload(name="Parent"), format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_requires_company_and_name(self):
        response = self.client.put(self.detail_url, {}, format="json")
        self.assert_invalid(response, "company")
        self.assertIn("name", response.data)

    def test_update_invalid_name(self):
        for name in ("", "   ", None, "x" * 256):
            with self.subTest(name=name):
                self.assert_invalid(self.client.patch(self.detail_url, {"name": name}, format="json"), "name")
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Parent")

    def test_update_rejects_duplicate_name(self):
        response = self.client.patch(self.detail_url, {"name": "Child"}, format="json")
        self.assert_invalid(response, "name")
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Parent")

    def test_update_company_checks_duplicate_name(self):
        Category.objects.create(company=self.other_company, name="Child")
        url = reverse("category-detail", args=[self.child.pk])
        response = self.client.patch(url, {"company": str(self.other_company.pk), "parent_category": None}, format="json")
        self.assert_invalid(response, "name")
        self.child.refresh_from_db()
        self.assertEqual(self.child.company, self.company)

    def test_update_rejects_invalid_related_ids(self):
        for field in ("company", "parent_category"):
            for value in ("invalid", str(uuid.uuid4())):
                with self.subTest(field=field, value=value):
                    response = self.client.patch(self.detail_url, {field: value}, format="json")
                    self.assert_invalid(response, field)

    def test_update_rejects_self_parent(self):
        response = self.client.patch(self.detail_url, {"parent_category": str(self.category.pk)}, format="json")
        self.assert_invalid(response, "parent_category")
        self.category.refresh_from_db()
        self.assertIsNone(self.category.parent_category)

    def test_update_rejects_descendant_parent(self):
        grandchild = Category.objects.create(company=self.company, name="Grandchild", parent_category=self.child)
        for descendant in (self.child, grandchild):
            with self.subTest(descendant=descendant.pk):
                response = self.client.patch(self.detail_url, {"parent_category": str(descendant.pk)}, format="json")
                self.assert_invalid(response, "parent_category")
        self.category.refresh_from_db()
        self.assertIsNone(self.category.parent_category)

    def test_update_parent(self):
        other_parent = Category.objects.create(company=self.company, name="Other parent")
        url = reverse("category-detail", args=[self.child.pk])
        response = self.client.patch(url, {"parent_category": str(other_parent.pk)}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.child.refresh_from_db()
        self.assertEqual(self.child.parent_category, other_parent)

    def test_update_clear_parent(self):
        url = reverse("category-detail", args=[self.child.pk])
        response = self.client.patch(url, {"parent_category": None}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.child.refresh_from_db()
        self.assertIsNone(self.child.parent_category)

    def test_update_rejects_parent_in_other_company(self):
        parent = Category.objects.create(company=self.other_company, name="Other parent")
        response = self.client.patch(self.detail_url, {"parent_category": str(parent.pk)}, format="json")
        self.assert_invalid(response, "parent_category")

    def test_update_company_rejects_existing_parent_in_other_company(self):
        url = reverse("category-detail", args=[self.child.pk])
        response = self.client.patch(url, {"company": str(self.other_company.pk)}, format="json")
        self.assert_invalid(response, "parent_category")

    def test_update_company_rejects_existing_children_in_other_company(self):
        response = self.client.patch(self.detail_url, {"company": str(self.other_company.pk)}, format="json")
        self.assert_invalid(response, "company")
        self.category.refresh_from_db()
        self.assertEqual(self.category.company, self.company)

    def test_update_company_with_parent_in_new_company(self):
        parent = Category.objects.create(company=self.other_company, name="Other parent")
        url = reverse("category-detail", args=[self.child.pk])
        response = self.client.patch(url, {"company": str(self.other_company.pk), "parent_category": str(parent.pk)}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.child.refresh_from_db()
        self.assertEqual(self.child.company, self.other_company)
        self.assertEqual(self.child.parent_category, parent)

    def test_update_ignores_read_only_fields(self):
        original_id = self.category.pk
        created_at = self.category.created_at
        response = self.client.patch(self.detail_url, {"id": str(uuid.uuid4()), "created_at": "2000-01-01T00:00:00Z", "updated_at": "2000-01-01T00:00:00Z"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.pk, original_id)
        self.assertEqual(self.category.created_at, created_at)
        self.assertNotEqual(self.category.updated_at.year, 2000)

    def test_destroy(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(pk=self.category.pk).exists())
        self.child.refresh_from_db()
        self.assertIsNone(self.child.parent_category)
        self.assertTrue(Company.objects.filter(pk=self.company.pk).exists())

    def test_missing_category(self):
        for pk in (uuid.uuid4(), "invalid"):
            url = reverse("category-detail", args=[pk])
            for method in ("get", "put", "patch", "delete"):
                with self.subTest(pk=pk, method=method):
                    response = getattr(self.client, method)(url, {}, format="json")
                    self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Category.objects.count(), 2)
