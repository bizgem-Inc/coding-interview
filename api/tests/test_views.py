"""
Category API ユニットテスト
URL: /api/categories/
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company


class CategoryViewTests(APITestCase):
    """テストデータの初期化（複数企業と階層構造の構築）"""
    def setUp(self):
        # 1社目とそのカテゴリセット（親子）
        self.company = Company.objects.create(name="My Company")
        self.parent_category = Category.objects.create(
            company=self.company,
            name="My Root Category",
        )
        self.child_category_1 = Category.objects.create(
            company=self.company,
            name="My Child Category",
            parent_category=self.parent_category
        )
        self.child_category_2 = Category.objects.create(
            company=self.company,
            name="My Child Category2",
            parent_category=self.parent_category
        )

        # 2社目とそのカテゴリセット
        self.other_company = Company.objects.create(name="Other Company")
        self.other_category = Category.objects.create(
            company=self.other_company,
            name="Other Root Category",
        )

        # 更新用の親なしカテゴリも用意
        self.original_category = Category.objects.create(
            company=self.other_company,
            name="Original Category",
        )

        self.list_url = reverse("category-list")
    """---------------取得系のテスト---------------"""
    """カテゴリ一覧取得の正常系テスト"""
    def test_list(self):
        response = self.client.get(self.list_url)

        # --- 検証 ---
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 全件（親+子）が返ってくることを確認
        self.assertEqual(len(response.data),5)
        self.assertEqual(str(response.data[0]["company"]), str(self.company.id))
    """単一カテゴリ詳細取得の正常系テスト"""
    def test_retrieve(self):    
        # My Child Category2 をターゲットとする
        target_id = self.child_category_2.id
        # URL発行→リクエスト実行
        url = reverse("category-detail", kwargs={"pk": target_id})
        response = self.client.get(url)

        # --- 検証 ---
        # ステータスコードが 200 OK であること
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # リクエストした ID と一致しているか確認
        self.assertEqual(str(response.data["id"]), str(target_id))
        # 名前も「My Child Category2」であることを確認する
        self.assertEqual(response.data["name"], "My Child Category2")
    """---------------作成系のテスト---------------"""
    """カテゴリ新規作成の正常系テスト"""
    def test_create(self):
        payload = {
            "company": str(self.company.id),
            "name": "New Category",
            "parent_category": str(self.parent_category.id),
        }

        response = self.client.post(self.list_url, payload, format="json")

        # --- 検証 ---
        # --- レスポンスのチェック ---
        self.assertEqual(response.status_code, 201) # 201 Created
        self.assertEqual(response.data["name"], payload["name"])
        self.assertEqual(str(response.data["company"]), str(payload["company"]))
        self.assertEqual(str(response.data["parent_category"]), str(payload["parent_category"]))
        # IDや日付が自動生成されているか
        self.assertIn("id", response.data)
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data) # ここで存在をチェック
        # --- データベースのチェック ---
        # response.data["id"] を使って、保存されたばかりの生データを取得
        saved_category = Category.objects.get(id=response.data["id"])
        
        self.assertEqual(saved_category.name, payload["name"])
        self.assertEqual(str(saved_category.company.id), str(payload["company"]))
        self.assertEqual(str(saved_category.parent_category.id), str(payload["parent_category"]))
        self.assertIsNotNone(saved_category.created_at)
        self.assertIsNotNone(saved_category.updated_at)
    """親カテゴリを指定しない（nullを許可する）場合の新規作成テスト（正常系）"""
    def test_create_without_parent_category(self):    
        payload = {
            "company": str(self.company.id),
            "name": "Standalone Category",
            "parent_category": None,
        }

        response = self.client.post(self.list_url, payload, format="json")

        # --- 検証 ---
        # parent_category が None でも正常に作成できることを確認
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data["parent_category"])
    """同名カテゴリの重複作成制限テスト（異常系）"""
    def test_create_duplicate_name_returns_bad_request(self):    
        payload = {
            "company": str(self.company.id),
            "name": "My Child Category",
            "parent_category": str(self.parent_category.id)
        }
        response = self.client.post(self.list_url, payload, format="json")

        # --- 検証 ---
        # 重複エラーにより400が返ることを確認
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # non_field_errors（特定の項目エラーではない）にエラーメッセージが入っていることを確認
        self.assertEqual(
            response.data["non_field_errors"][0], 
            "この会社には既に同じ名前のカテゴリーが存在します。"
        )
    """他社のカテゴリを親カテゴリに指定できないことのテスト（バリデーション確認1）"""
    def test_create_parent_category_from_other_company_returns_bad_request(self):    
        payload = {
            "company": str(self.company.id),
            "name": "Invalid Parent Category",
            "parent_category": str(self.other_category.id),
        }

        response = self.client.post(self.list_url, payload, format="json")

        # --- 検証 ---
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # parent_category フィールドにエラーが入っていることを確認
        self.assertIn("parent_category", response.data)
        self.assertEqual(
            response.data["parent_category"][0], 
            "親カテゴリーは同じ会社に所属している必要があります。"
        )
    """---------------更新系のテスト---------------"""
    """カテゴリ情報の更新テスト（正常系）"""
    def test_update(self):
        url = reverse("category-detail", kwargs={"pk": self.original_category.id})          
        # 自分の会社もあえて変更してみる（移管シナリオ）
        payload = {
            "name": "Updated Category",
            "parent_category": str(self.parent_category.id),
            "company": str(self.company.id),
        }
        
        # 検証用に更新前のタイムスタンプを保持
        old_created_at = self.original_category.created_at
        old_updated_at = self.original_category.updated_at

        response = self.client.patch(url, payload, format="json")

        # --- 検証 ---
        # 1. レスポンスのチェック
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], payload["name"])
        self.assertEqual(str(response.data["parent_category"]), payload["parent_category"])
        self.assertEqual(str(response.data["company"]), payload["company"])
        
        # 2. データベースのチェック
        self.original_category.refresh_from_db()
        self.assertEqual(self.original_category.name, payload["name"])
        self.assertEqual(str(self.original_category.parent_category.id), payload["parent_category"])
        self.assertEqual(str(self.original_category.company.id), payload["company"])
        self.assertGreater(self.original_category.updated_at, old_updated_at)
        self.assertEqual(self.original_category.created_at, old_created_at)
    """他社のカテゴリを親カテゴリに指定できないことのテスト（バリデーション確認1）"""
    def test_update_parent_category_from_other_company_returns_bad_request(self):
        url = reverse("category-detail", kwargs={"pk": self.original_category.id})


        # 他社のカテゴリを親に設定しようとする（PATCH）
        payload = {"parent_category": str(self.parent_category.id)}
        response = self.client.patch(url, payload, format="json")

        # --- 検証 ---
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # parent_category フィールドにエラーが入っていることを確認
        self.assertIn("parent_category", response.data)
        self.assertEqual(
            response.data["parent_category"][0], 
            "親カテゴリーは同じ会社に所属している必要があります。"
        )
    """自分自身を親カテゴリーに設定できないことのテスト（バリデーション確認2）"""
    def test_update_self_parent_returns_bad_request(self):
        url = reverse("category-detail", kwargs={"pk": self.original_category.id})
        response = self.client.patch(
            url,
            {"parent_category": str(self.original_category.id)},
            format="json",
        )

        # --- 検証 ---
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # parent_category フィールドにエラーが入っていることを確認
        self.assertIn("parent_category", response.data)
        self.assertEqual(
            response.data["parent_category"][0],
            "自身のカテゴリーを親に指定することはできません。"
        )

    """---------------削除系のテスト---------------"""
    """カテゴリ削除の正常系テスト"""
    def test_destroy(self):   
        url = reverse("category-detail", kwargs={"pk": self.original_category.id})

        response = self.client.delete(url)

        # --- 検証 ---
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # DBから完全に消えていることを確認
        self.assertFalse(Category.objects.filter(id=self.original_category.id).exists())
    """親を削除した場合、子が親になることを確認"""
    def test_destroy_parent_keeps_child_as_orphan(self):    
        #  親を削除
        url = reverse("category-detail", kwargs={"pk": self.parent_category.id})
        response = self.client.delete(url)
        
        # --- 検証 ---
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # 最新の状態をDBから再取得
        self.child_category_1.refresh_from_db() 
        self.child_category_2.refresh_from_db()
        # 子は生きているか
        self.assertTrue(Category.objects.filter(id=self.child_category_1.id).exists())
        self.assertTrue(Category.objects.filter(id=self.child_category_2.id).exists())
        # 親が NULL になっているか
        self.assertIsNone(self.child_category_1.parent_category)
        self.assertIsNone(self.child_category_2.parent_category)

    """---------------カスタムレスポンスのテスト---------------"""
    """名前が255文字を超えた時のカスタムエラーメッセージ検証"""
    def test_create_name_max_length_error_message(self):
        long_name = "a" * 256
        payload = {
            "company": str(self.company.id),
            "name": long_name,
            "parent_category": None,
        }
        response = self.client.post(self.list_url, payload, format="json")

        # --- 検証 ---
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # 指定したカスタムメッセージが返ってきているか
        self.assertEqual(
            response.data["name"][0], 
            "入力は255文字以内で入力してください。"
        )
    """名前が未入力の時のカスタムエラーメッセージ検証"""
    def test_create_name_required_error_message(self):

        payload = {
            "company": str(self.company.id),
            # "name" をあえて入れない
            "parent_category": None,
        }
        response = self.client.post(self.list_url, payload, format="json")

        # --- 検証 ---
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["name"][0], 
            "名前は必須です。"
        )
    """存在しない企業IDを指定した時のカスタムエラーメッセージ検証"""
    def test_create_company_does_not_exist_error_message(self):
        invalid_uuid = "00000000-0000-0000-0000-000000000000"
        payload = {
            "company": invalid_uuid,
            "name": "Valid Name",
            "parent_category": None,
        }
        response = self.client.post(self.list_url, payload, format="json")

        # --- 検証 ---
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # company フィールドの does_not_exist メッセージを検証
        self.assertEqual(
            response.data["company"][0], 
            "指定された企業が見つかりません。"
        )
    """企業が未入力（キー欠落）の時のカスタムエラーメッセージ検証"""
    def test_create_company_required_error_message(self):
        payload = {
            "name": "New Category",
            # "company" をあえて含めない
            "parent_category": None,
        }
        response = self.client.post(self.list_url, payload, format="json")

        # --- 検証 ---
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["company"][0], "企業は必須です。")