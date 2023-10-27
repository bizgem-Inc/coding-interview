<<<<<<< HEAD
from rest_framework.test import APITestCase


class CategoryViewTests(APITestCase):
    def test_list(self):
        pass

    def test_retrieve(self):
        pass

    def test_create(self):
        pass

    def test_update(self):
        pass

    def test_destroy(self):
        pass
=======
import datetime

from rest_framework.test import APITestCase
from ..models.category import Category
from ..models.company import Company

COMPANY_NAME_1 = "COM01"
COMPANY_NAME_2 = "COM02"
CATEGORY_NAME_1 = "CAT01"
CATEGORY_NAME_2 = "CAT02"
CATEGORY_NAME_3 = "CAT03"
CATEGORY_NAME_4 = "CAT04"
CATEGORY_NAME_5 = "CAT05"
TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
# テスト用データベースに category を書き込み後、テストされるまでに許容され時間・この時間を越えるとエラー
MAX_DERAY_TIME = datetime.timedelta(seconds=1) 

class CategoryViewTests(APITestCase):
    
    #
    # API から読みだした Category(json) のチェック
    #   created_at, updated_at については assertEqual() 実行時のMAX_DERAY_TIME以内の時刻であれば OK とする
    #   引数
    #       payload : API から読みだした Category(json)
    #       category : 比較対象の Category 
    #       ignore_id : True なら、id は比較しない
    #
    def check_category(self, payload: dict, category: Category, ignore_id=False):
        #  Category.id は正しいか？
        if not ignore_id:
            self.assertEqual(payload["id"], str(category.id))

        #  Company.company は正しいか？
        self.assertEqual(payload["company"]["id"], str(category.company.id))

        #  Category.name は正しいか？
        self.assertEqual(payload["name"], category.name)

        # Category.parent_category は正しいか？
        if category.parent_category is None or payload["parent_category"] is None:
            self.assertEqual(payload["parent_category"], category.parent_category)
        else:
            self.assertEqual(payload["parent_category"]["id"], str(category.parent_category.id))

        # Category.created_at は正しいか？(現在から1秒以内か)
        self.assertTrue(datetime.datetime.now() - datetime.datetime.strptime(payload["created_at"], TIME_FORMAT) < MAX_DERAY_TIME )

        # Category.created_at は正しいか？(現在から1秒以内か)
        self.assertTrue(datetime.datetime.now() - datetime.datetime.strptime(payload["updated_at"], TIME_FORMAT) < MAX_DERAY_TIME )


    #
    # テストごとの準備
    #   テスト用データベースに company x 2, category x 3 を書き込む
    #
    @classmethod
    def setUpTestData(cls):
        # Company_1 {name=COMPANY_NAME_1}
        # Company_2 {name=COMPANY_NAME_2}
        # Category_1 {name=CATEGORY_NAME_1, company=Company_1, parent_category=None}
        # Category_2 {name=CATEGORY_NAME_2, company=Company_2, parent_category=Category_1}
        # Category_2 {name=CATEGORY_NAME_3, company=Company_1, parent_category=Category_2}
        cls.company_1 = Company.objects.create(name=COMPANY_NAME_1)
        cls.company_2 = Company.objects.create(name=COMPANY_NAME_2)
        cls.category_1 = Category.objects.create(name=CATEGORY_NAME_1, company=cls.company_1, parent_category=None)
        cls.category_2 = Category.objects.create(name=CATEGORY_NAME_2, company=cls.company_2, parent_category=cls.category_1)
        cls.category_3 = Category.objects.create(name=CATEGORY_NAME_3, company=cls.company_1, parent_category=cls.category_2)

    #
    # GET 全部読み出し(list) のテスト
    #   すべての setUpTestData で書き込んだすべての Category をチェックする
    #   
    def test_list(self):
        # /api/category/ を実行
        response = self.client.get('/api/category/')
        self.assertEqual(200, response.status_code)
        payloads = response.json()

        # category_1 をチェック
        self.check_category(payloads[0], self.category_1)

        # category_2 をチェック
        self.check_category(payloads[1], self.category_2)

        # category_3 をチェック
        self.check_category(payloads[2], self.category_3)

        pass

    #
    # GET 個別指定・検索のテスト
    #   id, name, company.name, parent_category.name で検索できることを確認する
    #
    def test_retrieve(self):
        # /api/category/{id} のチェック
        # category_1 をチェック
        response = self.client.get('/api/category/'+str(self.category_1.id)+"/")
        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.check_category(payload, self.category_1)

        # category_2 をチェック
        response = self.client.get('/api/category/'+str(self.category_2.id)+"/")
        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.check_category(payload, self.category_2)

        # category_3 をチェック
        response = self.client.get('/api/category/'+str(self.category_3.id)+"/")
        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.check_category(payload, self.category_3)

        # /api/category/?name={name} のチェック
        response = self.client.get(
            '/api/category/',
            {'name': CATEGORY_NAME_3}
        )
        self.assertEqual(200, response.status_code)
        payloads = response.json()
        self.assertTrue(len(payloads) == 1)  # 読みだした Category は一つか？
        self.check_category(payloads[0], self.category_3)

        # /api/category/?company={name} のチェック
        response = self.client.get(
            '/api/category/',
            {'company': COMPANY_NAME_2}
        )
        self.assertEqual(200, response.status_code)
        payloads = response.json()
        self.assertTrue(len(payloads) == 1)  # 読みだした Category は一つか？
        self.check_category(payloads[0], self.category_2)

        # /api/category/?parent_category={name} のチェック
        response = self.client.get(
            '/api/category/',
            {'parent_category': CATEGORY_NAME_2}
        )
        self.assertEqual(200, response.status_code)
        payloads = response.json()
        self.assertTrue(len(payloads) == 1)  # 読みだした Category は一つか？
        self.check_category(payloads[0], self.category_3)

        pass

    #
    # POST のテスト
    #   parent_category 有り、無しの Category を一つずつ書き出し、読み込むテスト
    #
    def test_create(self):
        # parent_category 有りの Category のチェック
        # 書き込み
        response = self.client.post(
            '/api/category/',
            {
                'company.name' : str(self.company_2.name),
                'name' : CATEGORY_NAME_4,
                'parent_category.name' : str(self.category_2.name)
            }
        )
        self.assertEqual(201, response.status_code)

        # 書き込み内容のチェック
        # 比較データの作成
        category = Category(
            company=self.company_2,
            name=CATEGORY_NAME_4,
            parent_category=self.category_2,
        )
        # 書き込んだ Category の読み出し
        response = self.client.get(
            '/api/category/',
            {'name' : CATEGORY_NAME_4}
        )
        self.assertEqual(200, response.status_code)
        payloads = response.json()
        self.assertTrue(len(payloads) == 1)  # 読みだした Category は一つか？
        self.check_category(payloads[0], category, ignore_id = True)

        # parent_category 無しの Category のチェック
        # 書き込み
        response = self.client.post(
            '/api/category/',
            {
                'company.name' : str(self.company_1.name),
                'name' : CATEGORY_NAME_5,
            }
        )
        self.assertEqual(201, response.status_code)

        # 書き込み内容のチェック
        # 比較データの作成
        category = Category(
            company=self.company_1,
            name=CATEGORY_NAME_5,
        )
        # 書き込んだ Category の読み出し
        response = self.client.get(
            '/api/category/',
            {'name' : CATEGORY_NAME_5}
        )
        self.assertEqual(200, response.status_code)
        payloads = response.json()
        self.assertTrue(len(payloads) == 1)  # 読みだした Category は一つか？
        self.check_category(payloads[0], category, ignore_id = True)

        pass
    # 
    # PUT のテスト
    #   1.category_1 を上書き後、id を指定して読み出しチェックする
    #   2.category_2 の parent_category を消したあと、id を指定して読み出しチェックする
    #
    def test_update(self):
        # category_1 の上書きチェック
        # 更新前の crated_at, updated_at を退避
        before_created_at = self.category_1.created_at.strftime(TIME_FORMAT)
        before_updated_at = self.category_1.updated_at.strftime(TIME_FORMAT)
        response = self.client.put(
            '/api/category/'+str(self.category_1.id)+"/",
            {
                'company.name' : COMPANY_NAME_2,
                'name' : CATEGORY_NAME_1+"Modified",
                'parent_category.name' : CATEGORY_NAME_2
            }
        )
        self.assertEqual(200, response.status_code)
        # 変更内容のチェック
        # 比較データの作成
        category = Category(
            company=self.company_2,
            name=CATEGORY_NAME_1+"Modified",
            parent_category=self.category_2,
        )
        # 書き換えられたデータの読み出し
        response = self.client.get('/api/category/'+str(self.category_1.id)+"/")
        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.check_category(payload, category, ignore_id = True)
        # created_at が変更されていないことをチェック
        self.assertEqual(payload["created_at"], before_created_at)
        # updated_at が新しくなっていることをチェック
        self.assertTrue(payload["updated_at"] > before_updated_at)

        # category_2 の parent_category を消すチェック
        # 更新前の crated_at, updated_at を退避
        before_created_at = self.category_2.created_at.strftime(TIME_FORMAT)
        before_updated_at = self.category_2.updated_at.strftime(TIME_FORMAT)
        response = self.client.put(
            '/api/category/'+str(self.category_2.id)+"/",
            {
                'company.name' : self.category_2.company.name,
                'name' : CATEGORY_NAME_2+"Modified",
            }
        )
        self.assertEqual(200, response.status_code)
        # 変更内容のチェック
        # 比較データの作成
        category = Category(
            company=self.category_2.company,
            name=CATEGORY_NAME_2+"Modified",
        )
        # 書き換えられたデータの読み出し
        response = self.client.get('/api/category/'+str(self.category_2.id)+"/")
        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.check_category(payload, category, ignore_id = True)
        # created_at が変更されていないことをチェック
        self.assertEqual(payload["created_at"], before_created_at)
        # updated_at が新しくなっていることをチェック
        self.assertTrue(payload["updated_at"] > before_updated_at)

        pass

    #
    # 初期化で書き込んだ Category を一つずつ消していくテスト
    #
    def test_destroy(self):
        # /api/category/ を実行し、3レコードあることを確認
        response = self.client.get('/api/category/')
        self.assertEqual(200, response.status_code)
        payloads = response.json()
        self.assertTrue(len(payloads) == 3)      

        # category_2 を削除
        response = self.client.delete('/api/category/'+str(self.category_2.id)+"/")
        self.assertEqual(204, response.status_code)
        # category_1 の存在をチェック
        response = self.client.get('/api/category/'+str(self.category_1.id)+"/")
        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.check_category(payload, self.category_1)
        # category_2 の削除をチェック
        response = self.client.get('/api/category/'+str(self.category_2.id)+"/")
        self.assertEqual(404, response.status_code)
        # category_3 の存在をチェック
        response = self.client.get('/api/category/'+str(self.category_3.id)+"/")
        self.assertEqual(200, response.status_code)
        payload = response.json()

        # category_3.parent_category の category_2 は削除済みなので None を設定
        self.category_3.parent_category = None
        self.check_category(payload, self.category_3)


        # category_1 を削除
        response = self.client.delete('/api/category/'+str(self.category_1.id)+"/")
        self.assertEqual(204, response.status_code)
        # category_1 の削除をチェック
        response = self.client.get('/api/category/'+str(self.category_1.id)+"/")
        self.assertEqual(404, response.status_code)
        # category_2 の削除をチェック
        response = self.client.get('/api/category/'+str(self.category_2.id)+"/")
        self.assertEqual(404, response.status_code)
        # category_3 の存在をチェック
        response = self.client.get('/api/category/'+str(self.category_3.id)+"/")
        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.check_category(payload, self.category_3)


        # category_3 を削除
        response = self.client.delete('/api/category/'+str(self.category_3.id)+"/")
        self.assertEqual(204, response.status_code)
        # /api/category/ を実行し、すべてのレコードが削除されていることをチェック
        response = self.client.get('/api/category/')
        self.assertEqual(200, response.status_code)
        payloads = response.json()
        self.assertTrue(len(payloads) == 0)      

        pass
>>>>>>> upstream/master
