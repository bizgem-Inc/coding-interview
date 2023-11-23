from rest_framework.test import APITestCase
from rest_framework.response import Response
from django.urls import reverse
from django.db.utils import IntegrityError
from api.models.category import Category
from api.models.company import Company

# categoryに含まれる項目の一覧
items = ['id','company','name','parent_category','created_at','updated_at']

def create_company() -> Company:
    ''' テスト用company '''
    company = Company.objects.create(name='テスト会社')
    return company

def create_categories() -> [Category]:
    """
    category viewのテスト用データ
    """
    # comparyテストデータ生成。
    company_1 = create_company()

    # Categoryテストデータ生成
    category1 = Category.objects.create(company=company_1, name='テスト1', parent_category=None)
    category2 = Category.objects.create(company=company_1, name='テスト2', parent_category=category1)
    category3 = Category.objects.create(company=company_1, name='テスト3', parent_category=None)

    return [category1, category2, category3]


class CategoryViewTests(APITestCase):

    def test_setup(self):
        '''set up'''
        pass

    def test_list(self):
        '''一覧取得テスト'''

        # ゼロ件テスト。正常に接続できること
        url = reverse("category-list")
        response:Response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # 取得データ件数が一致すること
        self.assertEquals(len(response.data), 0)

        # データ準備
        categories: [Category] = create_categories()

        # 正常に接続できること
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # 取得データ件数が一致すること
        self.assertEquals(len(response.data), len(categories))

        # レスポンスの各レコードとcategoryの各レコードの比較検証
        idx:int = 0
        for category in categories:
            category: Category
            # 各項目が一致するか検証
            self.assertEquals(str(category.id), str(response.data[idx]["id"]))
            self.assertEquals(category.company.id, response.data[idx]["company"])
            self.assertEquals(str(category.name), str(response.data[idx]["name"]))
            if category.parent_category:
                self.assertEquals(str(category.parent_category.id), str(response.data[idx]["parent_category"]))
            else:
                self.assertEquals(str(None), str(response.data[idx]["parent_category"]))
            # ※created_at,updated_atは、dateutilのparserが使えないため今回は比較検証を見送り存在チェックのみとする。
            self.assertIn("created_at", response.data[idx])
            self.assertIn("updated_at", response.data[idx])

            # レスポンスに想定外のデータが含まれていないかチェック
            for data in response.data[idx]:
                self.assertIn(data, items)

            # categoryを次のレコードへ
            idx += 1

    def test_retrieve(self):
        '''明細取得テスト'''
        # データ準備
        categories: [Category] = create_categories()
        category = categories[1]

        # 正常に接続できること
        url = reverse("category-detail", args=[str(category.id)])
        response:Response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # 各項目が一致するか検証
        self.assertEquals(str(category.id), str(response.data["id"]))
        self.assertEquals(category.company.id, response.data["company"])
        self.assertEquals(str(category.name), str(response.data["name"]))
        self.assertEquals(str(category.parent_category.id), str(response.data["parent_category"]))
        # ※created_at,updated_atは、dateutilのparserが使えないため今回は比較検証を見送り存在チェックのみとする。
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data)

        # レスポンスに想定外のデータが含まれていないかチェック
        for data_key in response.data.keys():
            self.assertIn(data_key, items)

        # categoryテーブル存在するIDを指定しない場合、エラーとなること。
        url = reverse("category-detail", args=["aaa"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


    def test_create(self):
        '''追加テスト'''
        # データ準備
        company_1 = create_company()

        url = reverse("category-list")
        test_company_id = str(company_1.id)
        test_name = 'ああああああ'

        # 正常に追加されること
        response:Response = self.client.post(url,{
            'company': test_company_id,
            'name': test_name,
        })
        self.assertEqual(response.status_code, 201)

        categories: [Category] = Category.objects.all()
        self.assertEqual(len(categories), 1)

        for category in categories:
            category: Category
            # 各項目が一致するか検証
            # self.assertEquals(str(category.id), str(response.data["id"]))
            self.assertEquals(category.name, test_name)
            self.assertEquals(category.parent_category, None)
            # ※created_at,updated_atは、dateutilのparserが使えないため今回は比較検証を見送り存在チェックのみとする。
            self.assertTrue(hasattr(category, 'id'))
            self.assertTrue(hasattr(category, 'created_at'))
            self.assertTrue(hasattr(category, 'updated_at'))

        ##############################################
        # エラーケース (Companyがない)
        response = self.client.post(url,{
            'name': 'a',
        })
        self.assertEqual(response.status_code, 400)
        # エラーケース (Companyテーブルに存在しないidが指定されている)
        response = self.client.post(url,{
            'company': 'nasi',
            'name': 'a',
        })
        self.assertEqual(response.status_code, 400)
        # エラーケース (nameがない)
        response = self.client.post(url,{
            'company': test_company_id,
        })
        self.assertEqual(response.status_code, 400)
        # エラーケース (name > 255文字)
        response = self.client.post(url,{
            'company': test_company_id,
            'name': 'a'*256,
        })
        self.assertEqual(response.status_code, 400)
        # リミットケース (nameの文字数max255文字)
        response = self.client.post(url,{
            'company': test_company_id,
            'name': 'a'*255,
        })
        self.assertEqual(response.status_code, 201)
        # エラーケース (parent_categoryにテーブルに存在しないidが指定されている)
        response = self.client.post(url,{
            'company': test_company_id,
            'name': test_name,
            'parent_category': 'nasi',
        })
        self.assertEqual(response.status_code, 400)
        # 正常ケース (created_atに不正な日付データ。自動編集項目であるため入力値は無視される)
        response = self.client.post(url,{
            'company': test_company_id,
            'name': 'created_at-test',
            'created_at': 'error!',
        })
        self.assertEqual(response.status_code, 201)
        # 正常ケース (updated_atに不正な日付データ。自動編集項目であるため入力値は無視される)
        response = self.client.post(url,{
            'company': test_company_id,
            'name': 'updated_at-test',
            'updated_at': 'error!',
        })
        self.assertEqual(response.status_code, 201)
        # エラーケース(同名、同companyの場合重複エラー)
        try:
            response = self.client.post(url,{
                'company': test_company_id,
                'name': 'updated_at-test',
                'updated_at': 'error!',
            })
            self.assertTrue(False)  # 重複エラーが発生しなかった場合テスト結果をFailedにする。
        except IntegrityError as ie:
            self.assertTrue(True)  # 重複エラーが発生した場合テスト結果をOKにする。

    def test_update(self):
        '''更新テスト'''
        # データ準備
        categories: [Category] = create_categories()
        category1:Category = categories[0]
        category2:Category = categories[1]

        url = reverse("category-detail", args=[str(category2.id)])
        name_edit = 'name_edit'

        # category2のデータが正常に更新されること。
        response:Response = self.client.put(url,{
            'company': str(category1.company.id),
            'name': name_edit,
            # 'parent_category': str(category2.parent_category.id),
            'parent_category': "",
        })
        self.assertEqual(response.status_code, 200)
        # 更新後のcategory2を取得
        category2_after_change: Category = Category.objects.get(id=str(category2.id))
        # 更新後の各項目が想定のとおり更新されていることを確認
        self.assertEqual(str(category2_after_change.company.id), str(category1.company.id))
        self.assertEqual(category2_after_change.name, name_edit)
        self.assertIsNone(category2_after_change.parent_category)
        self.assertNotEqual(category2_after_change.updated_at, category2.updated_at)
        # created_atは更新されていないことを確認
        self.assertEqual(category2_after_change.created_at, category2.created_at)

        ###################################################
        # 存在しないurl(ID)の場合エラー
        url_nasi = reverse("category-detail", args=["aaa"])
        response:Response = self.client.put(url_nasi,{
            'company': str(category1.company.id),
            'name': name_edit,
            'parent_category': "",
        })
        self.assertEqual(response.status_code, 404)

        # エラーケース (Companyがない)
        response = self.client.put(url,{
            'name': name_edit + 'aaa',
        })
        self.assertEqual(response.status_code, 400)
        # エラーケース (Companyテーブルに存在しないidが指定されている)
        response = self.client.put(url,{
            'company': 'nasi',
            'name': name_edit + 'aaa',
        })
        self.assertEqual(response.status_code, 400)
        # エラーケース (nameがない)
        response = self.client.put(url,{
            'company': str(category1.company.id),
        })
        self.assertEqual(response.status_code, 400)
        # エラーケース (name > 255文字)
        response = self.client.put(url,{
            'company': str(category1.company.id),
            'name': 'a'*256,
        })
        self.assertEqual(response.status_code, 400)
        # リミットケース (nameの文字数max255文字)
        response = self.client.put(url,{
            'company': str(category1.company.id),
            'name': 'a'*255,
        })
        self.assertEqual(response.status_code, 200)
        # エラーケース (parent_categoryにテーブルに存在しないidが指定されている)
        response = self.client.put(url,{
            'company': str(category1.company.id),
            'name': name_edit + 'aaa',
            'parent_category': 'nasi',
        })
        self.assertEqual(response.status_code, 400)
        # 正常ケース (created_atに不正な日付データ。自動編集項目であるため入力値は無視される)
        response = self.client.put(url,{
            'company': str(category1.company.id),
            'name': 'created_at-test',
            'created_at': 'error!',
        })
        self.assertEqual(response.status_code, 200)
        # 正常ケース (updated_atに不正な日付データ。自動編集項目であるため入力値は無視される)
        response = self.client.put(url,{
            'company': str(category1.company.id),
            'name': 'created_at-test',
            'updated_at': 'error!',
        })
        self.assertEqual(response.status_code, 200)
        # エラーケース(同名、同companyの場合重複エラー)
        try:
            response = self.client.put(url,{
                'company': str(category1.company.id),
                'name': category1.name,
            })
            self.assertTrue(False)  # 重複エラーが発生しなかった場合テスト結果をFailedにする。
        except IntegrityError as ie:
            self.assertTrue(True)  # 重複エラーが発生した場合テスト結果をOKにする。


    def test_destroy(self):
        '''削除テスト'''
        # データ準備
        categories: [Category] = create_categories()
        category2:Category = categories[1]

        url = reverse("category-detail", args=[str(category2.id)])

        # ＜削除前＞
        # 該当データが存在していること
        category2_get = Category.objects.filter(id=str(category2.id))
        self.assertEqual(len(category2_get), 1)

        # ＜削除＞
        # category2のデータが正常に更新されること。
        response:Response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

        # ＜削除後＞
        # 該当データが削除されていること
        category2_after_delete = Category.objects.filter(id=str(category2.id))
        self.assertEqual(len(category2_after_delete), 0)
        # 該当データ以外は削除されず残っていること
        category2_after_delete = Category.objects.all()
        self.assertEqual(len(category2_after_delete), 2)

        #######################################
        # 存在しないurl(ID)の場合エラー
        url_nasi = reverse("category-detail", args=["aaa"])
        response:Response = self.client.delete(url_nasi)
        self.assertEqual(response.status_code, 404)
