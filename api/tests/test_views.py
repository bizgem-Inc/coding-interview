from rest_framework.test import APITestCase
from rest_framework import status

from api.models.company import Company
from api.models.category import Category


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="TestCo")

    def test_list(self):
        Category.objects.create(company=self.company, name="c1")
        Category.objects.create(company=self.company, name="c2")

        resp = self.client.get("/api/categories/")
        assert resp.status_code == status.HTTP_200_OK
        assert isinstance(resp.json(), list)
        assert len(resp.json()) == 2

    def test_retrieve(self):
        c = Category.objects.create(company=self.company, name="c")
        resp = self.client.get(f"/api/categories/{c.id}/")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["id"] == str(c.id)
        assert data["name"] == "c"

    def test_create(self):
        payload = {"company": str(self.company.id), "name": "new"}
        resp = self.client.post("/api/categories/", payload, format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        data = resp.json()
        assert data["name"] == "new"
        assert data["company"] == str(self.company.id)

    def test_update(self):
        c = Category.objects.create(company=self.company, name="old")
        resp = self.client.patch(f"/api/categories/{c.id}/", {"name": "updated"}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["name"] == "updated"

    def test_destroy(self):
        c = Category.objects.create(company=self.company, name="todel")
        resp = self.client.delete(f"/api/categories/{c.id}/")
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        assert not Category.objects.filter(id=c.id).exists()

