from rest_framework.test import APITestCase
from django.urls import reverse
from api.models import Category, Company

import uuid

class CategoryViewTests(APITestCase):
    def setUp(self):
        # Create test companies
        self.company1 = Company.objects.create(id=uuid.uuid4(), name="Test Company 1")
        self.company2 = Company.objects.create(id=uuid.uuid4(), name="Test Company 2")

        # 親カテゴリ
        self.parent_category1 = self.create_category("Parent Category 1", self.company1, None)
        self.parent_category2 = self.create_category("Parent Category 2", self.company1, None)
        self.parent_category3 = self.create_category("Parent Category 3", self.company1, None)
        # 別会社の親カテゴリ
        self.parent_category4 = self.create_category("Parent Category 4", self.company2, None)

        # 親カテゴリのないカテゴリ
        self.category1 = self.create_category("Category 1", self.company1, None)
        # 親カテゴリの下にあるカテゴリ
        self.category2 = self.create_category("Category 2", self.company1, self.parent_category1)
        self.category3 = self.create_category("Category 3", self.company1, self.parent_category1)
        # 別会社のカテゴリ
        self.category4 = self.create_category("Category 4", self.company2, None)
        self.category5 = self.create_category("Category 5", self.company2, self.parent_category4)
        self.category6 = self.create_category("Category 6", self.company2, self.parent_category4)

    def test_list(self):
        """
            カテゴリ一覧取得。
            6つのカテゴリと4つの親カテゴリが存在することを確認。
        """
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 10)
        self.assertEqual(['Category 1', 'Category 2', 'Category 3', 'Category 4', 'Category 5', 'Category 6', 'Parent Category 1', 'Parent Category 2', 'Parent Category 3', 'Parent Category 4'], [cat['name'] for cat in sorted(response.data, key=lambda x: x['name'])])


    def test_list_filter_by_parent_category(self):
        """
            親カテゴリでフィルタリング。
            Parent Category 1の下にあるカテゴリが2つ存在することを確認。
        """
        url = reverse('category-list') + '?parent_category=' + str(self.parent_category1.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], "Category 2")
        self.assertEqual(response.data[1]['name'], "Category 3")

    def test_filter_by_company(self):
        """
            会社でフィルタリング。
            Company 1の親カテゴリ3つとカテゴリが3つ存在することを確認。
        """
        url = reverse('category-list') + '?company=' + str(self.company1.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 6)
        self.assertEqual(['Category 1', 'Category 2', 'Category 3', 'Parent Category 1', 'Parent Category 2', 'Parent Category 3'], [cat['name'] for cat in sorted(response.data, key=lambda x: x['name'])])

    def test_retrieve(self):
        """
            カテゴリ詳細取得。
            Category 1は親カテゴリなしで、Company 1に属することを確認。
            Category 2はParent Category 1の下にあり、Company 1に属することを確認。
        """
        url = reverse('category-detail', kwargs={'pk': self.category1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], "Category 1")
        self.assertEqual(response.data['company'], self.company1.id)
        self.assertEqual(response.data['company_name'], self.company1.name)
        self.assertIsNone(response.data['parent_category'])
        url = reverse('category-detail', kwargs={'pk': self.category2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], "Category 2")
        self.assertEqual(response.data['company'], self.company1.id)
        self.assertEqual(response.data['company_name'], self.company1.name)
        self.assertEqual(response.data['parent_category'], self.parent_category1.id)
        self.assertEqual(response.data['parent_category_name'], self.parent_category1.name)

    def test_retrieve_category_not_exists(self):
        """
            カテゴリ詳細取得。
            存在しないカテゴリを取得しようとすると404エラーが発生することを確認。
        """
        url = reverse('category-detail', kwargs={'pk': uuid.uuid4()})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(str(response.data['detail']), 'No Category matches the given query.')

    def test_create(self):
        """
            カテゴリ作成試験。
            新しいカテゴリをCompany 1の下にParent Category 1の下に作成することを確認。
        """
        url = reverse('category-list')
        data = {
            'name': 'New Category',
            'company': str(self.company1.id),
            'parent_category': str(self.parent_category1.id)
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assert_category_details(response.data['id'], 'New Category', self.company1.id, self.parent_category1.id)

    def test_create_no_parent(self):
        """
            カテゴリ作成試験。親カテゴリなしで新しいカテゴリをCompany 1の下に作成することを確認。
        """
        url = reverse('category-list')
        data = {
            'name': 'New Category',
            'company': str(self.company1.id),
            'parent_category': None
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assert_category_details(response.data['id'], 'New Category', self.company1.id, None)

    def test_create_parent_not_exist(self):
        """
            カテゴリ作成試験。親カテゴリが存在しない場合
        """
        url = reverse('category-list')
        data = {
            'name': 'New Category',
            'company': str(self.company1.id),
            'parent_category': uuid.uuid4()
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_create_no_company(self):
        """
            カテゴリ作成試験。会社なしで新しいカテゴリを作成することはできないことを確認。
        """
        url = reverse('category-list')
        data = {
            'name': 'New Category',
            'company': None,
            'parent_category': str(self.parent_category1.id)
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_create_duplicate_category(self):
        """
            カテゴリ作成試験。同じ会社と名前のカテゴリが既に存在する場合はエラーが発生することを確認。
        """
        url = reverse('category-list')
        data = {
            'name': 'Category 1',
            'company': str(self.company1.id),
            'parent_category': None
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(str(response.data['non_field_errors'][0]), 'The fields company, name must make a unique set.')

    def test_create_parent_category_mismatch(self):
        """
            カテゴリ作成試験。親カテゴリの企業IDとカテゴリの企業IDが一致しない場合はエラーが発生することを確認。
        """
        url = reverse('category-list')
        data = {
            'name': 'New Category',
            'company': str(self.company1.id),
            'parent_category': str(self.parent_category4.id)
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(str(response.data['non_field_errors'][0]), "Parent category must belong to the same company.")

    def test_create_category_name_max_length(self):
        """
            カテゴリ作成試験。カテゴリ名の最大長を超える場合はエラーが発生することを確認。
        """
        url = reverse('category-list')
        # 255文字のカテゴリ名は許可されるが、256文字は許可されない
        data = {
            'name': 'a' * 255,  # 255文字のカテゴリ名
            'company': str(self.company1.id),
            'parent_category': None
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)

        data = {
            'name': 'a' * 256,  # 256文字のカテゴリ名
            'company': str(self.company1.id),
            'parent_category': None
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('name', response.data)

    def test_create_category_name_required(self):
        """
            カテゴリ作成試験。カテゴリ名が必須であることを確認。
        """
        url = reverse('category-list')
        data = {
            'company': str(self.company1.id),
            'parent_category': None
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('name', response.data)

        data = {
            'name': '',  # 空のカテゴリ名
            'company': str(self.company1.id),
            'parent_category': None
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('name', response.data)

    def test_create_company_required(self):
        """
            カテゴリ作成試験。会社が必須であることを確認。
        """
        url = reverse('category-list')
        data = {
            'name': 'New Category',
            'parent_category': None
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

        data = {
            'name': 'New Category',
            'company': None,
            'parent_category': None
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_update_category_name(self):
        """
            カテゴリ更新試験。カテゴリ名称
        """
        url = reverse('category-detail', kwargs={'pk': self.category1.id})
        data = {
            'name': 'Updated Category',
            'company': str(self.company1.id),
            'parent_category': str(self.parent_category1.id)
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assert_category_details(self.category1.id, 'Updated Category', self.company1.id, self.parent_category1.id)

    def test_update_category_name(self):
        """
            カテゴリ更新試験。会社と親カテゴリを変更することを確認。
        """
        url = reverse('category-detail', kwargs={'pk': self.category1.id})
        data = {
            'name': 'Category 1',
            'company': str(self.company2.id),
            'parent_category': str(self.parent_category4.id)
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assert_category_details(self.category1.id, 'Category 1', self.company2.id, self.parent_category4.id)

    def test_update_category_name1(self):
        """
            カテゴリ更新試験。会社と親カテゴリが一致しない場合はエラー１
        """
        url = reverse('category-detail', kwargs={'pk': self.category1.id})
        data = {
            'name': 'Category 1',
            'company': str(self.company2.id),
            'parent_category': str(self.parent_category2.id)
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_update_category_name2(self):
        """
            カテゴリ更新試験。会社と親カテゴリが一致しない場合はエラー２
        """
        url = reverse('category-detail', kwargs={'pk': self.category1.id})
        data = {
            'name': 'Category 1',
            'company': str(self.company1.id),
            'parent_category': str(self.parent_category4.id)
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_update_category_name_max_length(self):
        """
            カテゴリ更新試験。カテゴリ名の最大長を超える場合はエラーが発生することを確認。
        """
        url = reverse('category-detail', kwargs={'pk': self.category1.id})
        data = {
            'name': 'a' * 255,  # 255文字のカテゴリ名
            'company': str(self.company1.id),
            'parent_category': None
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)

        data = {
            'name': 'a' * 256,  # 256文字のカテゴリ名
            'company': str(self.company1.id),
            'parent_category': None
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('name', response.data)

    def test_update_category_name_required(self):
        """
            カテゴリ更新試験。カテゴリ名が必須であることを確認。
        """
        url = reverse('category-detail', kwargs={'pk': self.category1.id})
        data = {
            'company': str(self.company1.id),
            'parent_category': None
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('name', response.data)

        data = {
            'name': '',  # 空のカテゴリ名
            'company': str(self.company1.id),
            'parent_category': None
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('name', response.data)

    def test_update_company_required(self):
        """
            カテゴリ更新試験。会社が必須であることを確認。
        """
        url = reverse('category-detail', kwargs={'pk': self.category1.id})
        data = {
            'name': 'Updated Category',
            'parent_category': None
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 400)

        data = {
            'name': 'Updated Category',
            'company': None,
            'parent_category': None
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_destroy(self):
        """
            カテゴリ削除試験。Category 1を削除し、存在しないことを確認。
        """
        url = reverse('category-detail', kwargs={'pk': self.category1.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Category.objects.filter(id=self.category1.id).exists())

    def test_destroy_category_not_exists(self):
        """
            カテゴリ削除試験。存在しないカテゴリを削除しようとするとエラーが発生することを確認。
        """
        url = reverse('category-detail', kwargs={'pk': uuid.uuid4()})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(str(response.data['detail']), 'No Category matches the given query.')

    def test_destroy_parent_category(self):
        """
            親カテゴリ削除試験。親カテゴリを削除し、関連する子カテゴリが親なしになることを確認。
        """
        url = reverse('category-detail', kwargs={'pk': self.parent_category1.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        # 親カテゴリが存在しないことを確認
        url = reverse('category-detail', kwargs={'pk': self.parent_category1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(str(response.data['detail']), 'No Category matches the given query.')

        # 子カテゴリの親がNoneになっていることを確認
        self.assert_category_details(self.category2.id, 'Category 2', self.company1.id, None)
        self.assert_category_details(self.category3.id, 'Category 3', self.company1.id, None)


    def create_category(self, name, company, parent_category=None):
        """
            Helper method to create a category.
        """
        return Category.objects.create(
            id=uuid.uuid4(),
            name=name,
            company=company,
            parent_category=parent_category
        )

    def assert_category_details(self, category_id, name, company, parent_category_id=None):
        """
        Helper method to assert category details.
        """
        url = reverse('category-detail', kwargs={'pk': category_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], name)
        self.assertEqual(response.data['company'], company)
        self.assertEqual(response.data['parent_category'], parent_category_id)
