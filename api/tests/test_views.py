import datetime
import json

from rest_framework.test import APITestCase
from ..models.category import Category
from ..models.company import Company

COMPANY_NAME_1 = "COM01"
COMPANY_NAME_2 = "COM02"
CATEGORY_NAME_1 = "CAT01"
CATEGORY_NAME_2 = "CAT02"
TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
# テスト用データベースに category を書き込み後、テストされるまでに許容され時間
MAX_DERAY_TIME = datetime.timedelta(seconds=1) 

class CategoryViewTests(APITestCase):
    category_1 = 0
    category_2 = 0
    category_3 = 0

    #
    # API から読みだした Category と db の Category のテスト
    #   created_at, updated_at については assertEqual() 実行時の一秒以内の時刻であれば OK とする
    #   引数
    #       payload : API から読みだした Category
    #       category : db の Category 
    #
    def check_category(self, payload: dict, category: Category):
        #  Category.id は正しいか？
        self.assertEqual(payload['id'], str(category.id))
        #  Company.company は正しいか？
        self.assertEqual(payload["company"]["id"], str(category.company.id))
        #  Category.name は正しいか？
        self.assertEqual(payload["name"], category.name)
        # Category.parent_category は正しいか？
        if category.parent_category is None:
            self.assertEqual(payload["parent_category"], category.parent_category)
        else:
            self.assertEqual(payload["parent_category"]["id"], str(category.parent_category.id))
        # Category.created_at は正しいか？(現在から1秒以内か)
        self.assertTrue(datetime.datetime.now() - datetime.datetime.strptime(payload["created_at"], TIME_FORMAT) < MAX_DERAY_TIME )
        # Category.created_at は正しいか？(現在から1秒以内か)
        self.assertTrue(datetime.datetime.now() - datetime.datetime.strptime(payload["updated_at"], TIME_FORMAT) < MAX_DERAY_TIME )


    @classmethod
    def setUpTestData(cls):
        # テスト用データベースに company, category を二つずつ書き込む
        # Company_1 {name=COMPANY_NAME_1}
        # Company_2 {name=COMPANY_NAME_2}
        # Category_1 {name=CATEGORY_NAME_1, company=Company_1, parent_category=None}
        # Category_2 {name=CATEGORY_NAME_2, company=Company_2, parent_category=Category_1}
        company_1 = Company.objects.create(name=COMPANY_NAME_1)
        company_2 = Company.objects.create(name=COMPANY_NAME_2)
        cls.category_1 = Category.objects.create(name=CATEGORY_NAME_1, company=company_1, parent_category=None)
        cls.category_2 = Category.objects.create(name=CATEGORY_NAME_2, company=company_2, parent_category=cls.category_1)
    

    def test_list(self):
        # /api/category/ のテスト

        # /api/category/ を実行
        response = self.client.get('/api/category/')
        self.assertEqual(200, response.status_code)
        payload = response.json()

        # 一つ目の category をチェック
        company = Company.objects.get(name=COMPANY_NAME_1)
        self.check_category(payload[0], self.category_1)

        # 二つ目の category をチェック
        company = Company.objects.get(name=COMPANY_NAME_2)
        self.check_category(payload[1], self.category_2)

        pass


    def test_retrieve(self):
        # /api/category/{id}/ のテスト

        # 一つ目の category をチェック
        response = self.client.get('/api/category/'+str(self.category_1.id)+"/")
        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.check_category(payload, self.category_1)

        # 二つ目の category をチェック
        response = self.client.get('/api/category/'+str(self.category_2.id)+"/")
        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.check_category(payload, self.category_2)

        pass

    def test_create(self):
        pass

    def test_update(self):
        pass

    def test_destroy(self):
        pass



