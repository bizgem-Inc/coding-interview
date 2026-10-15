import uuid

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company


class CategoryViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(name="Company")
        cls.other_company = Company.objects.create(name="Other company")
        cls.parent = Category.objects.create(company=cls.company, name="Parent")
        cls.category = Category.objects.create(
            company=cls.company, name="Child", parent_category=cls.parent
        )
        cls.other_category = Category.objects.create(company=cls.other_company, name="Other")

    def setUp(self):
        self.list_url = reverse("category-list")
        self.detail_url = reverse("category-detail", args=[self.category.pk])

    def payload(self, **overrides):
        data = {"company": str(self.company.pk), "name": "New category"}
        data.update(overrides)
        return data

    def test_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(
            [item["id"] for item in response.data],
            [str(self.parent.pk), str(self.category.pk), str(self.other_category.pk)],
        )

    def test_empty_list(self):
        Category.objects.all().delete()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_retrieve(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {
            "id": str(self.category.pk),
            "company": str(self.company.pk),
            "name": "Child",
            "parent_category": str(self.parent.pk),
            "created_at": self.category.created_at.isoformat().replace("+00:00", "Z"),
            "updated_at": self.category.updated_at.isoformat().replace("+00:00", "Z"),
        })

    def test_create(self):
        response = self.client.post(self.list_url, self.payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        category = Category.objects.get(pk=response.data["id"])
        self.assertEqual(category.company, self.company)
        self.assertEqual(category.name, "New category")
        self.assertIsNone(category.parent_category)
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data)

    def test_create_with_parent(self):
        response = self.client.post(
            self.list_url, self.payload(parent_category=str(self.parent.pk)), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.get(pk=response.data["id"]).parent_category, self.parent)

    def test_create_with_null_parent(self):
        response = self.client.post(
            self.list_url, self.payload(parent_category=None), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(Category.objects.get(pk=response.data["id"]).parent_category)

    def test_update(self):
        original_created_at = self.category.created_at
        original_updated_at = self.category.updated_at
        response = self.client.put(
            self.detail_url, self.payload(name="Renamed", parent_category=None), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Renamed")
        self.assertIsNone(self.category.parent_category)
        self.assertEqual(self.category.created_at, original_created_at)
        self.assertGreater(self.category.updated_at, original_updated_at)

    def test_partial_update(self):
        response = self.client.patch(self.detail_url, {"name": "Renamed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Renamed")
        self.assertEqual(self.category.company, self.company)
        self.assertEqual(self.category.parent_category, self.parent)

    def test_update_parent(self):
        response = self.client.patch(
            reverse("category-detail", args=[self.other_category.pk]),
            {"company": str(self.company.pk), "parent_category": str(self.parent.pk)},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.other_category.refresh_from_db()
        self.assertEqual(self.other_category.company, self.company)
        self.assertEqual(self.other_category.parent_category, self.parent)

    def test_update_with_unchanged_name(self):
        response = self.client.patch(self.detail_url, {"name": "Child"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_destroy(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(pk=self.category.pk).exists())
        self.assertTrue(Category.objects.filter(pk=self.parent.pk).exists())
        self.assertTrue(Company.objects.filter(pk=self.company.pk).exists())

    def test_destroy_parent_keeps_children(self):
        response = self.client.delete(reverse("category-detail", args=[self.parent.pk]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.category.refresh_from_db()
        self.assertIsNone(self.category.parent_category)

    def test_unknown_or_malformed_id_returns_not_found(self):
        for pk in [uuid.uuid4(), "invalid-uuid"]:
            url = reverse("category-detail", args=[pk])
            for method in ["get", "put", "patch", "delete"]:
                with self.subTest(pk=pk, method=method):
                    response = getattr(self.client, method)(url, {}, format="json")
                    self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_required_fields(self):
        for data, field in [({}, "company"), ({"company": str(self.company.pk)}, "name")]:
            with self.subTest(data=data):
                response = self.client.post(self.list_url, data, format="json")
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(field, response.data)
        response = self.client.put(self.detail_url, {"name": "Renamed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("company", response.data)

    def test_invalid_fields_do_not_create_or_update(self):
        invalid_values = {
            "name": ["", "   ", None, "x" * 256],
            "company": [None, str(uuid.uuid4()), "invalid-uuid"],
            "parent_category": [str(uuid.uuid4()), "invalid-uuid"],
        }
        for field, values in invalid_values.items():
            for value in values:
                for method, url in [("post", self.list_url), ("patch", self.detail_url)]:
                    with self.subTest(field=field, value=value, method=method):
                        count = Category.objects.count()
                        data = self.payload(**{field: value}) if method == "post" else {field: value}
                        response = getattr(self.client, method)(url, data, format="json")
                        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                        self.assertIn(field, response.data)
                        self.assertEqual(Category.objects.count(), count)
                        self.category.refresh_from_db()
                        self.assertEqual(self.category.name, "Child")
                        self.assertEqual(self.category.company, self.company)
                        self.assertEqual(self.category.parent_category, self.parent)

    def test_name_max_length(self):
        response = self.client.post(self.list_url, self.payload(name="x" * 255), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_duplicate_name_in_same_company(self):
        for method, url in [("post", self.list_url), ("put", self.detail_url), ("patch", self.detail_url)]:
            with self.subTest(method=method):
                response = getattr(self.client, method)(url, self.payload(name="Parent"), format="json")
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn("non_field_errors", response.data)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Child")

    def test_same_name_in_different_companies(self):
        response = self.client.post(
            self.list_url, self.payload(company=str(self.other_company.pk), name="Parent"), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_company_only_update_checks_uniqueness(self):
        Category.objects.create(company=self.other_company, name="Child")
        response = self.client.patch(
            self.detail_url, {"company": str(self.other_company.pk), "parent_category": None}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_parent_from_another_company(self):
        for method, url in [("post", self.list_url), ("put", self.detail_url), ("patch", self.detail_url)]:
            with self.subTest(method=method):
                response = getattr(self.client, method)(
                    url, self.payload(parent_category=str(self.other_category.pk)), format="json"
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn("parent_category", response.data)

    def test_company_change_checks_existing_parent_and_children(self):
        for category, field in [(self.category, "parent_category"), (self.parent, "company")]:
            with self.subTest(category=category):
                response = self.client.patch(
                    reverse("category-detail", args=[category.pk]),
                    {"company": str(self.other_company.pk)}, format="json",
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(field, response.data)
                category.refresh_from_db()
                self.assertEqual(category.company, self.company)

    def test_self_parent_and_descendant_parent_are_rejected(self):
        grandchild = Category.objects.create(
            company=self.company, name="Grandchild", parent_category=self.category
        )
        for parent in [self.parent, self.category, grandchild]:
            with self.subTest(parent=parent):
                response = self.client.patch(
                    reverse("category-detail", args=[self.parent.pk]),
                    {"parent_category": str(parent.pk)}, format="json",
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn("parent_category", response.data)
        self.parent.refresh_from_db()
        self.assertIsNone(self.parent.parent_category)

    def test_generated_fields_are_read_only(self):
        supplied_id = str(uuid.uuid4())
        supplied_time = "2000-01-01T00:00:00Z"
        generated_fields = {"id": supplied_id, "created_at": supplied_time, "updated_at": supplied_time}
        response = self.client.post(
            self.list_url, self.payload(**generated_fields), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(response.data["id"], supplied_id)
        self.assertNotEqual(response.data["created_at"], supplied_time)
        self.assertNotEqual(response.data["updated_at"], supplied_time)
        original_created_at = self.category.created_at
        response = self.client.patch(self.detail_url, generated_fields, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(str(self.category.pk), response.data["id"])
        self.assertEqual(self.category.created_at, original_created_at)
        self.assertNotEqual(response.data["updated_at"], supplied_time)
