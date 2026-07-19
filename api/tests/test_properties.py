import string
import uuid

from django.db import IntegrityError, transaction
from hypothesis import given, settings, strategies as st
from hypothesis.extra.django import TestCase
from rest_framework.test import APIClient

from api.models import Category, Company


category_names = st.text(alphabet=string.ascii_letters + string.digits + "-_", min_size=1, max_size=255)


class CategoryPropertyTests(TestCase):
    @settings(max_examples=25)
    @given(name=category_names)
    def test_category_name_is_unique_within_a_company(self, name):
        company = Company.objects.create(name=f"Company-{uuid.uuid4()}")
        Category.objects.create(company=company, name=name)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Category.objects.create(company=company, name=name)

    @settings(max_examples=25)
    @given(name=category_names)
    def test_category_name_can_be_reused_by_another_company(self, name):
        first_company = Company.objects.create(name=f"Company-{uuid.uuid4()}")
        second_company = Company.objects.create(name=f"Company-{uuid.uuid4()}")

        Category.objects.create(company=first_company, name=name)
        category = Category.objects.create(company=second_company, name=name)

        self.assertEqual(category.name, name)
        self.assertEqual(category.company_id, second_company.id)

    @settings(max_examples=25)
    @given(names=st.lists(category_names, min_size=2, max_size=2, unique=True))
    def test_deleting_a_parent_category_clears_the_child_reference(self, names):
        parent_name, child_name = names
        company = Company.objects.create(name=f"Company-{uuid.uuid4()}")
        parent = Category.objects.create(company=company, name=parent_name)
        child = Category.objects.create(company=company, name=child_name, parent_category=parent)

        parent.delete()
        child.refresh_from_db()

        self.assertIsNone(child.parent_category)

    @settings(max_examples=25)
    @given(name=category_names)
    def test_create_api_round_trips_valid_category_names(self, name):
        company = Company.objects.create(name=f"Company-{uuid.uuid4()}")
        client = APIClient()

        create_response = client.post(
            "/api/categories/",
            {"company": str(company.id), "name": name},
            format="json",
        )

        self.assertEqual(create_response.status_code, 201)
        retrieve_response = client.get(f"/api/categories/{create_response.data['id']}/")
        self.assertEqual(retrieve_response.status_code, 200)
        self.assertEqual(retrieve_response.data["name"], name)
        self.assertEqual(retrieve_response.data["company"], company.id)
