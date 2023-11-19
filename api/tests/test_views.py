from rest_framework.test import APITestCase, APIClient
from .factories import CategoryFactory, CompanyFactory
from api.models.category import Category
from django.conf import settings
from rest_framework import status
import uuid
from datetime import date


class CategoryViewTests(APITestCase):

    @classmethod
    def setUpClass(cls):
        # roleをテスト共通として作成しておく
        cls.url = "/api/categories/"
        cls.client = APIClient()
        cls.date_format = settings.DATETIME_FORMAT
        super().setUpClass()

    def _to_date_string(self, date: date):
        return date.strftime(self.date_format)

    def test_list_成功(self):

        data_size = 5

        # ダミーデータ作成
        [CategoryFactory() for _ in range(data_size)]

        response = self.client.get(self.url)
        response_data = response.data

        # ステータスコード
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # データ数
        self.assertEqual(response_data["count"], data_size)

        expected_data = Category.objects.order_by('pk')
        actual_data = sorted(response_data['results'], key=lambda x: x["id"])

        # データの内容の正誤
        for expected, actual in zip(expected_data, actual_data):
            self.assertEqual(actual["id"], str(expected.id))
            self.assertEqual(actual["name"], expected.name)

            if actual["parent_category_id"]:
                self.assertEqual(actual["parent_category_id"],
                                 expected.parent_category.id)
            self.assertEqual(actual["company_id"], expected.company.id)
            self.assertEqual(actual["created_at"],
                             self._to_date_string(expected.created_at))
            self.assertEqual(actual["updated_at"],
                             self._to_date_string(expected.updated_at))

    def test_retrieve_親カテゴリなし_成功(self):
        # ダミーデータ作成
        expected = CategoryFactory()
        expected = Category.objects.get(pk=expected.id)

        response = self.client.get(f"{self.url}{expected.id}/")
        response_data = response.data

        # ステータスコード
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # データの中身
        self._assert_retrieve_response(response_data, expected)

    def test_retrieve_親カテゴリあり_成功(self):
        # ダミーデータ作成
        expected = CategoryFactory()
        expected = Category.objects.get(pk=expected.id)

        response = self.client.get(f"{self.url}{expected.id}/")
        response_data = response.data

        # ステータスコード
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # データの中身
        self._assert_retrieve_response(response_data, expected)

    def _assert_retrieve_response(self, actual, expected):

        self.assertEqual(actual["id"], str(expected.id))
        self.assertEqual(actual["name"], expected.name)
        self.assertEqual(actual["created_at"],
                         self._to_date_string(expected.created_at))
        self.assertEqual(actual["updated_at"],
                         self._to_date_string(expected.updated_at))

        actual_company, expected_company = actual["company"], expected.company

        self.assertEqual(actual_company["id"], str(expected_company.id))
        self.assertEqual(actual_company["name"], expected_company.name)
        self.assertEqual(actual_company["created_at"],
                         self._to_date_string(expected_company.created_at))
        self.assertEqual(actual_company["updated_at"],
                         self._to_date_string(expected_company.updated_at))

        if expected.parent_category:
            actual_parent, expected_parent = \
                actual["parent_category"], expected.parent_category
            self.assertEqual(actual_parent["id"], str(expected_parent.id))
            self.assertEqual(actual_parent["name"], expected_parent.name)
            self.assertEqual(actual_parent["created_at"],
                             self._to_date_string(expected_parent.created_at))
            self.assertEqual(actual_parent["updated_at"],
                             self._to_date_string(expected_parent.updated_at))

    def test_retrieve_不正なuuid_失敗(self):
        # ダミーデータ作成
        CategoryFactory()

        response = self.client.get(f"{self.url}{str(uuid.uuid4)}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_不正な文字列_失敗(self):
        # ダミーデータ作成
        CategoryFactory()

        response = self.client.get(f"{self.url}aaaaa/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_正しいnameとcompany_idを設定_成功(self):
        company = CompanyFactory()
        param = {
            "name": "create_test",
            "companyId": str(company.id),
        }
        base_count = Category.objects.all().count()
        response = self.client.post(self.url, param)
        response_data = response.data

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 1レコード作成されていること
        self.assertEqual(base_count+1, Category.objects.all().count())
        expected = Category.objects.get(pk=response_data["id"])
        self.assertEqual(param["name"], expected.name)
        self.assertEqual(param["companyId"], str(expected.company.id))

    def test_create_正しいnameとcompany_idとparent_category_idを設定_成功(self):
        company = CompanyFactory()
        parent_category = CategoryFactory()
        param = {
            "name": "create_test",
            "companyId": str(company.id),
            "parentCategoryId": str(parent_category.id)
        }
        base_count = Category.objects.all().count()
        response = self.client.post(self.url, param)
        response_data = response.data

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 1レコード作成されていること
        self.assertEqual(base_count+1, Category.objects.all().count())
        expected = Category.objects.get(pk=response_data["id"])
        self.assertEqual(param["name"], expected.name)
        self.assertEqual(param["companyId"], str(expected.company.id))
        self.assertEqual(param["parentCategoryId"],
                         str(expected.parent_category.id))

    def test_create_正しいnameと不正なcompany_idを設定_失敗(self):
        param = {
            "name": "create_test",
            "companyId": str(uuid.uuid4()),
        }
        response = self.client.post(self.url, param)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_正しいnameとcompany_idと不正なparent_cateotry_idを設定_失敗(self):
        company = CompanyFactory()

        param = {
            "name": "create_test",
            "companyId": str(company.id),
            "parentCategoryId": str(uuid.uuid4())
        }
        response = self.client.post(self.url, param)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_正しいid_正しいname_成功(self):
        category = CategoryFactory()

        param = {
            "name": "update_test",
        }
        response = self.client.put(f"{self.url}{category.id}/", param)
        actual = Category.objects.get(pk=category.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(actual.name, param["name"])

    def test_update_正しいid_正しいnameとcompanyIdとparentCategoryId_成功(self):
        category = CategoryFactory()
        company = CompanyFactory()
        parent_category = CategoryFactory()

        param = {
            "name": "update_test",
            "companyId": str(company.id),
            "parentCategoryId": str(parent_category.id),
        }
        response = self.client.put(f"{self.url}{category.id}/", param)
        actual = Category.objects.get(pk=category.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(actual.name, param["name"])
        self.assertEqual(str(actual.company.id), company.id)
        self.assertEqual(str(actual.parent_category.id), parent_category.id)

    def test_update_正しいid_不正なcompanyId_失敗(self):
        category = CategoryFactory()

        param = {
            "name": "update_test",
            "companyId": str(uuid.uuid4())
        }
        response = self.client.put(f"{self.url}{category.id}/", param)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_destroy_正しいid_成功(self):
        category = CategoryFactory()

        response = self.client.delete(f"{self.url}{category.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Category.DoesNotExist):
            Category.objects.get(pk=category.id)

    def test_destroy_不正なid_失敗(self):
        response = self.client.delete(f"{self.url}{uuid.uuid4()}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
