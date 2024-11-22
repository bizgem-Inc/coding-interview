from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory
from django.urls import reverse
from ..models.company import Company
from ..models.category import Category
from ..views.category import CategoryViewSet

class CategoryViewTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.com = Company.objects.create(name='company')
        cls.cat1 = Category.objects.create(name='category1', company=cls.com)
        cls.cat2 = Category.objects.create(name='category2',company=cls.com, parent_category=cls.cat1)

    def test_list(self):
        url = reverse('category-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], self.cat1.name)
        self.assertEqual(response.data[1]['name'], self.cat2.name)
        self.assertEqual(str(response.data[1]['parent_category']), response.data[0]['id'])

    def test_retrieve(self):
        firstCat = Category.objects.get(name=self.cat1.name)
        url = reverse('category-detail',args=[firstCat.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], firstCat.name)

    def test_create(self):
        beforeCount = Category.objects.count()
        url = reverse('category-list')
        newCat = {"company": self.com.id, "name": "new_category"}
        response = self.client.post(url, newCat, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], 'new_category')
        self.assertEqual(Category.objects.count(), beforeCount + 1)

    def test_update(self):
        secondCat = Category.objects.get(name=self.cat2.name)
        url = reverse('category-detail',args=[secondCat.id])
        modifiedCat = {"company": secondCat.company.id, "name": "modified", "parent_category": None}
        response = self.client.put(url, modifiedCat, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Category.objects.get(id=secondCat.id).name, "modified")
        self.assertEqual(Category.objects.get(id=secondCat.id).parent_category, None)

    def test_destroy(self):
        beforeCount = Category.objects.count()
        firstCat = Category.objects.get(name=self.cat1.name)
        url = reverse('category-detail',args=[firstCat.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Category.objects.count(), beforeCount - 1)

