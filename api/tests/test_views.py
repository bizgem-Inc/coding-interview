from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from api.models import Company, Category


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
        self.assertEqual(response.data[0]['name'], self.category.name)
        self.assertEqual(response.data[1]['name'], self.son_category.name)
        self.assertEqual(response.data[0]['id'], self.category.id.__str__())
        self.assertEqual(response.data[1]['id'], self.son_category.id.__str__())

    def test_retrieve(self):
        response = self.client.get(self.detail_url(self.category.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Shoes')
        self.assertEqual(response.data['id'], self.category.id.__str__())

    def test_create(self):
        created_category = {
            "name": "Yeezy Boost",
            "company": self.company.id,
            "parent_category": self.son_category.id
        }
        response = self.client.post(self.list_url, created_category, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 3)
        self.assertTrue(Category.objects.filter(name="Yeezy Boost").exists())

    def test_update(self):
        updated_category = {
            "name": "Updated Adidas",
            "company": self.company.id
        }
        response = self.client.put(self.detail_url(self.category.id), updated_category, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Updated Adidas")

    def test_destroy(self):
        response = self.client.delete(self.detail_url(self.son_category.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.son_category.id).exists())
        self.assertFalse(Category.objects.filter(parent_category=self.son_category.id).exists())

    def test_category_without_name(self):
        response = self.client.post(
            self.list_url,
            {"company": self.company.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['name'][0], 'This field is required.')

    def test_diff_company(self):
        new_company = Company.objects.create(
            name="Nike"
        )
        created_category = {
            "name": "Yeezy Boost",
            "company": new_company.id,
            "parent_category": self.son_category.id
        }
        response = self.client.post(self.list_url, created_category, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['parent_category'][0], 'parent_category must belong to the same company.')

    def test_parent_category_from_diff_company(self):
        new_company = Company.objects.create(
            name="Nike"
        )
        new_category = Category.objects.create(
            name="Shoes",
            company=new_company
        )
        updated_son_category = {
            "name": "Updated Yeezy",
            "company": self.company.id,
            "parent_category": new_category.id
        }
        response = self.client.put(self.detail_url(self.son_category.id), updated_son_category, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['parent_category'][0], 'parent_category must belong to the same company.')

    def test_self_as_parent(self):
        updated_son_category = {
            "name": "Updated Yeezy",
            "company": self.company.id,
            "parent_category": self.son_category.id
        }
        response = self.client.put(self.detail_url(self.son_category.id), updated_son_category, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['parent_category'][0], 'A category cannot be its own parent.')

    def test_parent_category_cycle(self):
        updated_category = {
            "name": "Updated Adidas",
            "company": self.company.id,
            "parent_category": self.son_category.id
        }
        response = self.client.put(self.detail_url(self.category.id), updated_category, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)
