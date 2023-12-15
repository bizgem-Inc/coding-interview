import uuid
from django.urls import reverse
from rest_framework.test import APITestCase
from ..models import Category, Company

class CategoryViewTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.company_1 = Company.objects.create(name="test_company_1")
        cls.company_2 = Company.objects.create(name="test_company_2")
        cls.category_1 = Category.objects.create(name="test_category_1", company=cls.company_1)
        cls.category_2 = Category.objects.create(name="test_category_2", company=cls.company_1, parent_category=cls.category_1)
        cls.category_3 = Category.objects.create(name="test_category_3", company=cls.company_1)

    def test_list(self):
        url = reverse("api:category-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_retrieve(self):
        pk = self.category_1.id
        # 正常系
        url = reverse("api:category-detail", kwargs={'pk': pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('id'), str(self.category_1.id))

        # 異常系
        # 存在しないidを指定
        pk = uuid.uuid4()
        url = reverse("api:category-detail", kwargs={'pk': pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_create(self):
        url = reverse("api:category-list")

        # 正常系
        # parent_category_idがnullの場合
        params = {
            "name": "create_category_test_1",
            "company_id": self.company_1.id,
            "parent_category_id": None,
        }
        response = self.client.post(url, params, format='json')
        self.assertEqual(response.status_code, 201)

        # parent_category_idを指定した場合
        params = {
            "name": "create_category_test_2",
            "company_id": self.company_1.id,
            "parent_category_id": self.category_1.id,
        }
        response = self.client.post(url, params, format='json')
        self.assertEqual(response.status_code, 201)

        # 異常系
        # nameが255文字を超えている場合(256文字)
        params = {
            "name": "1123456789011234567890112345678901123456789011234567890112345678901123456789011234567890112345678901123456789011234567890112345678901123456789011234567890112345678901123456789011234567890112345678901123456789011234567890112345678901123456789011234567890123",
            "company_id": self.company_1.id,
            "parent_category_id": None,
        }
        response = self.client.post(url, params, format='json')
        self.assertEqual(response.status_code, 400)

        # nameがブランクの場合
        params = {
            "name": "",
            "company_id": self.company_1.id,
            "parent_category_id": None,
        }
        response = self.client.post(url, params, format='json')
        self.assertEqual(response.status_code, 400)

        # company_idが不正な場合
        params = {
            "name": "create_category_test_3",
            "company_id": uuid.uuid4(),
            "parent_category_id": None,
        }
        response = self.client.post(url, params, format='json')
        self.assertEqual(response.status_code, 400)

        # parent_category_idが不正
        params = {
            "name": "create_category_test_4",
            "company_id": self.company_1.id,
            "parent_category_id": uuid.uuid4(),
        }
        response = self.client.post(url, params, format='json')
        self.assertEqual(response.status_code, 400)

        # 親を持っているcategoryをparent_category_idに指定した場合
        params = {
            "name": "create_category_test_5",
            "company_id": self.company_1.id,
            "parent_category_id": self.category_2.id,
        }
        response = self.client.post(url, params, format='json')
        self.assertEqual(response.status_code, 400)

        # comapyとnameで重複している場合
        params = {
            "name": "test_category_1",
            "company_id": self.company_1.id,
            "parent_category_id": None,
        }
        response = self.client.post(url, params, format='json')
        self.assertEqual(response.status_code, 400)

    def test_update(self):
        pk = self.category_2.id
        url = reverse("api:category-detail", kwargs={'pk': pk})

        # 正常系
        # PUT
        # nameを更新
        params = {
            "name": "test_category_2_1",
            "company_id": self.category_2.company.id,
            "parent_category_id": self.category_2.parent_category.id,
        }
        response = self.client.put(url, params, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('name'), 'test_category_2_1')

        # company_idを更新
        params = {
            "name": "test_category_2_1",
            "company_id": self.company_1.id,
            "parent_category_id": self.category_2.parent_category.id,
        }
        response = self.client.put(url, params, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('company').get('id'), str(self.company_1.id))

        # parent_category_idを更新
        params = {
            "name": "test_category_2_1",
            "company_id": self.company_1.id,
            "parent_category_id": None,
        }
        response = self.client.put(url, params, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('parent_category'), None)

        # PATCH
        # nameを更新
        params = {
            "name": "test_category_2_2",
        }
        response = self.client.patch(url, params, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('name'), 'test_category_2_2')

        # company_idを更新
        params = {
            "company_id": self.company_2.id,
        }
        response = self.client.patch(url, params, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('company').get('id'), str(self.company_2.id))

        # parent_category_idを更新
        params = {
            "parent_category_id": self.category_1.id,
        }
        response = self.client.patch(url, params, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('parent_category').get('id'), str(self.category_1.id))

        # 異常系
        pk = self.category_1.id
        url = reverse("api:category-detail", kwargs={'pk': pk})

        # nameが255文字を超えている場合(256文字)
        params = {
            "name": "1123456789011234567890112345678901123456789011234567890112345678901123456789011234567890112345678901123456789011234567890112345678901123456789011234567890112345678901123456789011234567890112345678901123456789011234567890112345678901123456789011234567890123"
        }
        response = self.client.patch(url, params, format='json')
        self.assertEqual(response.status_code, 400)

        # nameがブランクの場合
        params = {
            "name": ""
        }
        response = self.client.patch(url, params, format='json')
        self.assertEqual(response.status_code, 400)

        # company_idが不正な場合
        params = {
            "company_id": uuid.uuid4(),
        }
        response = self.client.patch(url, params, format='json')
        self.assertEqual(response.status_code, 400)

        # parent_category_idが不正
        params = {
            "parent_category_id": uuid.uuid4()
        }
        response = self.client.patch(url, params, format='json')
        self.assertEqual(response.status_code, 400)

        # 親を持っているcategoryをparent_category_idに指定した場合
        params = {
            "parent_category_id": self.category_2.id
        }
        response = self.client.patch(url, params, format='json')
        self.assertEqual(response.status_code, 400)

        # parent_category_idに自分自身を設定
        params = {
            "parent_category_id": pk,
        }
        response = self.client.patch(url, params, format='json')
        self.assertEqual(response.status_code, 400)

        # comapyとnameで重複しているもので更新しようとした場合
        params = {
            "name": "test_category_3",
            "company_id": self.category_3.company.id,
        }
        response = self.client.patch(url, params, format='json')
        self.assertEqual(response.status_code, 400)

    def test_destroy(self):
        pk = self.category_1.id
        url = reverse("api:category-detail", kwargs={'pk': pk})

        # 正常系
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

        # 異常系
        # 存在しないIDを削除
        pk = uuid.uuid4()
        url = reverse("api:category-detail", kwargs={'pk': pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)
