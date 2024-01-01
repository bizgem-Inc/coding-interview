from rest_framework import status
from rest_framework.test import APITestCase

def create_company(client):
    return client.post("/api/companies/", {"name": "test"}, format="json")


class CompanyViewTests(APITestCase):
    def test_create(self):
        response = create_company(self.client)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list(self):
        self.test_create()
        response = self.client.get("/api/companies/", format="json")
        self.assertEqual(len(response.data), 1)
        return response.data

    def test_retrieve(self):
        data = self.test_list()
        id = data[0].get("id")
        self.assertEqual(len(id), 36)
        response = self.client.get(f"/api/companies/{id}", format="json", follow=True)
        self.assertEqual(response.data.get("id"), id)
        return id

    def test_update(self):
        id = self.test_retrieve()
        response = self.client.put(f"/api/companies/{id}/", {"name": "test2"}, format="json", follow=True)
        self.assertEqual(response.data.get("name"), "test2")

    def test_destroy(self):
        id = self.test_retrieve()
        response = self.client.delete(f"/api/companies/{id}/", format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

class CategoryViewTests(APITestCase):
    def test_create(self):
        company = create_company(self.client)
        response = self.client.post("/api/categories/", {"company": company.data.get("id"), "name": "test"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list(self):
        self.test_create()
        response = self.client.get("/api/categories/", format="json")
        self.assertEqual(len(response.data), 1)
        return response.data

    def test_retrieve(self):
        data = self.test_list()
        id = data[0].get("id")
        company_id = data[0].get("company")
        self.assertEqual(len(id), 36)
        response = self.client.get(f"/api/categories/{id}", format="json", follow=True)
        self.assertEqual(response.data.get("id"), id)
        return (id, company_id)

    def test_update(self):
        id, company_id = self.test_retrieve()
        response = self.client.put(f"/api/categories/{id}/", {"name": "test2", "company": company_id}, format="json", follow=True)
        self.assertEqual(response.data.get("name"), "test2")

    def test_destroy(self):
        id, _ = self.test_retrieve()
        response = self.client.delete(f"/api/categories/{id}/", format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
