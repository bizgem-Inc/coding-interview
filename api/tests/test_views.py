from rest_framework.test import APITestCase


class CategoryViewTests(APITestCase):
    def test_list(self):
        from api.models import Company, Category
        
        company = Company.objects.create(name="テスト企業")
        category1 = Category.objects.create(company=company, name="カテゴリ1")
        category2 = Category.objects.create(company=company, name="カテゴリ2")
        
        # APIエンドポイントへのGETリクエスト
        response = self.client.get('/api/categories/')
        
        # レスポンスのステータスコードを確認
        self.assertEqual(response.status_code, 200)
        
        # レスポンスデータの検証
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], 'カテゴリ1')
        self.assertEqual(response.data[1]['name'], 'カテゴリ2')

    def test_retrieve(self):
        from api.models import Company, Category
        
        company = Company.objects.create(name="テスト企業")
        category = Category.objects.create(company=company, name="カテゴリ1")
        
        # APIエンドポイントへのGETリクエスト
        response = self.client.get(f'/api/categories/{category.id}/')
        
        # レスポンスのステータスコードを確認
        self.assertEqual(response.status_code, 200)
        
        # レスポンスデータの検証
        self.assertEqual(response.data['name'], 'カテゴリ1')
        self.assertEqual(response.data['company'], str(company.id))

    def test_create(self):
        from api.models import Company, Category
        
        company = Company.objects.create(name="テスト企業")
        
        # POSTリクエストのデータを準備
        data = {
            'company': str(company.id),
            'name': 'カテゴリ1'
        }
        
        # APIエンドポイントへのPOSTリクエスト
        response = self.client.post('/api/categories/', data, format='json')
        
        # レスポンスのステータスコードを確認
        self.assertEqual(response.status_code, 201)
        
        # レスポンスデータの検証
        self.assertEqual(response.data['name'], 'カテゴリ1')
        self.assertEqual(response.data['company'], str(company.id))
        
        # データベースに保存されたことを確認
        self.assertEqual(Category.objects.count(), 1)
        category = Category.objects.first()
        self.assertEqual(category.name, 'カテゴリ1')
        self.assertEqual(str(category.company.id), str(company.id))

    def test_update(self):
        from api.models import Company, Category
        
        company = Company.objects.create(name="テスト企業")
        category = Category.objects.create(company=company, name="カテゴリ1")
        
        # PUTリクエストのデータを準備
        data = {
            'company': str(company.id),
            'name': 'カテゴリ2'
        }
        
        # APIエンドポイントへのPUTリクエスト
        response = self.client.put(f'/api/categories/{category.id}/', data, format='json')
        
        # レスポンスのステータスコードを確認
        self.assertEqual(response.status_code, 200)
        
        # レスポンスデータの検証
        self.assertEqual(response.data['name'], 'カテゴリ2')
        self.assertEqual(response.data['company'], str(company.id))
        
        # データベースの値が更新されたことを確認
        category.refresh_from_db()
        self.assertEqual(category.name, 'カテゴリ2')
        self.assertEqual(str(category.company.id), str(company.id))

    def test_destroy(self):
        from api.models import Company, Category
        
        company = Company.objects.create(name="テスト企業")
        category = Category.objects.create(company=company, name="カテゴリ1")
        
        # APIエンドポイントへのDELETEリクエスト
        response = self.client.delete(f'/api/categories/{category.id}/')
        
        # レスポンスのステータスコードを確認
        self.assertEqual(response.status_code, 204)
        
        # データベースからデータが削除されたことを確認
        self.assertEqual(Category.objects.count(), 0)
