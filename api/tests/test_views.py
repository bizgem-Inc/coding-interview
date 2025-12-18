from django.urls import NoReverseMatch, reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.company import Company
from api.models.category import Category


def _reverse(name, kwargs=None):
    kwargs = kwargs or {}
    try:
        return reverse(f"api:{name}", kwargs=kwargs)
    except NoReverseMatch:
        return reverse(name, kwargs=kwargs)


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="ACME")
        self.other_company = Company.objects.create(name="Other Inc.")

        self.cat1 = Category.objects.create(company=self.company, name="Food")
        self.cat2 = Category.objects.create(company=self.company, name="Drink", parent_category=self.cat1)

    def test_list(self):
        url = _reverse("category-list")
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # pagination入ってない想定: listがそのまま返る
        self.assertIsInstance(res.data, list)
        self.assertEqual(len(res.data), 2)

    def test_retrieve(self):
        url = _reverse("category-detail", kwargs={"pk": str(self.cat2.id)})
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["id"], str(self.cat2.id))
        self.assertEqual(res.data["name"], "Drink")
        self.assertEqual(res.data["company"], str(self.company.id))
        self.assertEqual(res.data["parent_category"], str(self.cat1.id))

    def test_create(self):
        url = _reverse("category-list")
        payload = {
            "company": str(self.company.id),
            "name": "Snack",
            "parent_category": str(self.cat1.id),
        }

        res = self.client.post(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(id=res.data["id"]).exists())
        self.assertEqual(res.data["name"], "Snack")
        self.assertEqual(res.data["company"], str(self.company.id))

    def test_update(self):
        url = _reverse("category-detail", kwargs={"pk": str(self.cat1.id)})
        payload = {"name": "Foods"}  # PATCHで軽く

        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.cat1.refresh_from_db()
        self.assertEqual(self.cat1.name, "Foods")

    def test_destroy(self):
        url = _reverse("category-detail", kwargs={"pk": str(self.cat2.id)})

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.cat2.id).exists())
