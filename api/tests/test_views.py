from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from api.models import Company, Category
import uuid


class CategoryViewTests(APITestCase):

    def setUp(self):
        self.company = Company.objects.create(
            name="Adidas"
        )
        self.category = Category.objects.create(
            name="Shoes",
            company=self.company
        )
        self.son_category = Category.objects.create(
            name="Yeezy",
            company=self.company,
            parent_category=self.category
        )
        self.list_url = reverse('category-list')
        self.detail_url = lambda pk: reverse('category-detail', args=[pk])

    def test_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], 'Shoes')
        self.assertEqual(response.data[1]['name'], 'Yeezy')

    def test_retrieve(self):
        response = self.client.get(self.detail_url(self.category.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Shoes')

    def test_create(self):
        created_data = {
            "name": "Yeezy Boost",
            "company": str(self.company.id),
            "parent_category": self.son_category.id
        }
        response = self.client.post(self.list_url, created_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 3)
        self.assertTrue(Category.objects.filter(name="Yeezy Boost").exists())

    def test_update(self):
        update_data = {
            "name": "Updated Adidas",
            "company": str(self.company.id)
        }
        response = self.client.put(self.detail_url(self.category.id), update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Updated Adidas")

    def test_destroy(self):
        response = self.client.delete(self.detail_url(self.son_category.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.son_category.id).exists())
        self.assertFalse(Category.objects.filter(parent_category=self.son_category.id).exists())
