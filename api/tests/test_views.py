from rest_framework import status
from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company


class CategoryViewTests(APITestCase):
    """カテゴリーのe2eテスト"""

    def setUp(self):
        """各テストの前に実行される共通のセットアップ"""
        # テスト用の企業を作成
        self.company1 = Company.objects.create(name="テスト企業1")
        self.company2 = Company.objects.create(name="テスト企業2")

        # テスト用のカテゴリを作成
        self.category1 = Category.objects.create(
            company=self.company1,
            name="カテゴリ1",
            parent_category=None
        )
        self.category2 = Category.objects.create(
            company=self.company1,
            name="カテゴリ2",
            parent_category=self.category1
        )
        self.category3 = Category.objects.create(
            company=self.company2,
            name="カテゴリ3",
            parent_category=None
        )

    def test_list(self):
        """【正常系】カテゴリ一覧取得のテスト (GET /api/categories/)"""
        # APIリクエスト
        url = "/api/categories/"
        response = self.client.get(url)

        # ステータスコードの確認
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # レスポンスデータの確認
        self.assertEqual(len(response.data), 3)

        # データの内容を確認
        category_ids = [cat["id"] for cat in response.data]
        self.assertIn(str(self.category1.id), category_ids)
        self.assertIn(str(self.category2.id), category_ids)
        self.assertIn(str(self.category3.id), category_ids)

    def test_retrieve(self):
        """【正常系】カテゴリ取得のテスト (GET /api/categories/{id}/)"""
        # APIリクエスト
        url = f"/api/categories/{self.category1.id}/"
        response = self.client.get(url)

        # ステータスコードの確認
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # レスポンスデータの確認
        self.assertEqual(str(response.data["id"]), str(self.category1.id))
        self.assertEqual(response.data["name"], "カテゴリ1")
        self.assertEqual(str(response.data["company"]), str(self.company1.id))
        self.assertIsNone(response.data["parent_category"])
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data)

    def test_create(self):
        """【正常系】カテゴリ作成のテスト (POST /api/categories/)"""
        # リクエストデータ
        data = {
            "company": str(self.company1.id),
            "name": "新規カテゴリ",
            "parent_category": None
        }

        # APIリクエスト
        url = "/api/categories/"
        response = self.client.post(url, data, format="json")

        # ステータスコードの確認
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # レスポンスデータの確認
        self.assertEqual(response.data["name"], "新規カテゴリ")
        self.assertEqual(str(response.data["company"]), str(self.company1.id))
        self.assertIsNone(response.data["parent_category"])
        self.assertIn("id", response.data)
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data)

        # データベースに保存されていることを確認
        created_category = Category.objects.get(id=response.data["id"])
        self.assertEqual(created_category.name, "新規カテゴリ")
        self.assertEqual(created_category.company, self.company1)

    def test_create_with_parent_category(self):
        """【正常系】親カテゴリを指定したカテゴリ作成のテスト"""
        # リクエストデータ（親カテゴリを指定）
        data = {
            "company": str(self.company1.id),
            "name": "子カテゴリ",
            "parent_category": str(self.category1.id)
        }

        # APIリクエスト
        url = "/api/categories/"
        response = self.client.post(url, data, format="json")

        # ステータスコードの確認
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # レスポンスデータの確認
        self.assertEqual(response.data["name"], "子カテゴリ")
        self.assertEqual(str(response.data["company"]), str(self.company1.id))
        self.assertEqual(str(response.data["parent_category"]), str(self.category1.id))

        # データベースに正しく保存されていることを確認
        created_category = Category.objects.get(id=response.data["id"])
        self.assertEqual(created_category.parent_category, self.category1)

    def test_update(self):
        """【正常系】カテゴリ全体更新のテスト (PUT /api/categories/{id}/)"""
        # リクエストデータ
        data = {
            "company": str(self.company1.id),
            "name": "更新されたカテゴリ1",
            "parent_category": None
        }

        # APIリクエスト
        url = f"/api/categories/{self.category1.id}/"
        response = self.client.put(url, data, format="json")

        # ステータスコードの確認
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # レスポンスデータの確認
        self.assertEqual(str(response.data["id"]), str(self.category1.id))
        self.assertEqual(response.data["name"], "更新されたカテゴリ1")
        self.assertEqual(str(response.data["company"]), str(self.company1.id))

        # データベースが更新されていることを確認
        self.category1.refresh_from_db()
        self.assertEqual(self.category1.name, "更新されたカテゴリ1")

    def test_update_with_parent_category(self):
        """【正常系】親カテゴリを変更する全体更新のテスト"""
        # category3をcategory1の子カテゴリに変更（異なる企業なので新しい親を作成）
        # まず同じ企業の別のカテゴリを作成
        new_parent = Category.objects.create(
            company=self.company2,
            name="新しい親カテゴリ"
        )

        # リクエストデータ
        data = {
            "company": str(self.company2.id),
            "name": "更新されたカテゴリ3",
            "parent_category": str(new_parent.id)
        }

        # APIリクエスト
        url = f"/api/categories/{self.category3.id}/"
        response = self.client.put(url, data, format="json")

        # ステータスコードの確認
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # レスポンスデータの確認
        self.assertEqual(str(response.data["parent_category"]), str(new_parent.id))

        # データベースが更新されていることを確認
        self.category3.refresh_from_db()
        self.assertEqual(self.category3.parent_category, new_parent)

    def test_partial_update(self):
        """【正常系】カテゴリ部分更新のテスト (PATCH /api/categories/{id}/)"""
        # リクエストデータ（名前のみ更新）
        data = {
            "name": "部分更新されたカテゴリ"
        }

        # APIリクエスト
        url = f"/api/categories/{self.category1.id}/"
        response = self.client.patch(url, data, format="json")

        # ステータスコードの確認
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # レスポンスデータの確認
        self.assertEqual(response.data["name"], "部分更新されたカテゴリ")
        self.assertEqual(str(response.data["company"]), str(self.company1.id))  # 変更されていない

        # データベースが更新されていることを確認
        self.category1.refresh_from_db()
        self.assertEqual(self.category1.name, "部分更新されたカテゴリ")
        self.assertEqual(self.category1.company, self.company1)  # 変更されていない

    def test_partial_update_parent_category(self):
        """【正常系】親カテゴリのみを部分更新するテスト"""
        # 新しい親カテゴリを作成
        new_parent = Category.objects.create(
            company=self.company1,
            name="新しい親"
        )

        # リクエストデータ（親カテゴリのみ更新）
        data = {
            "parent_category": str(new_parent.id)
        }

        # APIリクエスト
        url = f"/api/categories/{self.category1.id}/"
        response = self.client.patch(url, data, format="json")

        # ステータスコードの確認
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # レスポンスデータの確認
        self.assertEqual(str(response.data["parent_category"]), str(new_parent.id))
        self.assertEqual(response.data["name"], "カテゴリ1")  # 変更されていない

        # データベースが更新されていることを確認
        self.category1.refresh_from_db()
        self.assertEqual(self.category1.parent_category, new_parent)

    def test_partial_update_remove_parent_category(self):
        """【正常系】親カテゴリを削除する部分更新のテスト"""
        # category2は元々category1を親に持っている
        self.assertIsNotNone(self.category2.parent_category)

        # リクエストデータ（親カテゴリをnullに設定）
        data = {
            "parent_category": None
        }

        # APIリクエスト
        url = f"/api/categories/{self.category2.id}/"
        response = self.client.patch(url, data, format="json")

        # ステータスコードの確認
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # レスポンスデータの確認
        self.assertIsNone(response.data["parent_category"])

        # データベースが更新されていることを確認
        self.category2.refresh_from_db()
        self.assertIsNone(self.category2.parent_category)

    def test_destroy(self):
        """【正常系】カテゴリ削除のテスト (DELETE /api/categories/{id}/)"""
        # 削除前にカテゴリが存在することを確認
        self.assertTrue(Category.objects.filter(id=self.category1.id).exists())

        # APIリクエスト
        url = f"/api/categories/{self.category1.id}/"
        response = self.client.delete(url)

        # ステータスコードの確認
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # データベースから削除されていることを確認
        self.assertFalse(Category.objects.filter(id=self.category1.id).exists())

    def test_destroy_category_with_children(self):
        """【正常系】子カテゴリを持つカテゴリの削除テスト"""
        # category1は子カテゴリ(category2)を持っている
        self.assertTrue(Category.objects.filter(parent_category=self.category1).exists())

        # APIリクエスト
        url = f"/api/categories/{self.category1.id}/"
        response = self.client.delete(url)

        # ステータスコードの確認
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # 親カテゴリが削除されていることを確認
        self.assertFalse(Category.objects.filter(id=self.category1.id).exists())

        # 子カテゴリの親がNullに設定されていることを確認（SET_NULLの動作）
        self.category2.refresh_from_db()
        self.assertIsNone(self.category2.parent_category)

    # ========================================
    # 異常系テスト
    # ========================================

    # 名前（name）のバリデーションエラー

    def test_create_with_empty_name(self):
        """【異常系】空文字のカテゴリ名で作成"""
        data = {
            "company": str(self.company1.id),
            "name": "",
            "parent_category": None
        }

        url = "/api/categories/"
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"][0], "カテゴリ名は必須です。")

    def test_create_with_whitespace_only_name(self):
        """【異常系】スペースのみのカテゴリ名で作成"""
        data = {
            "company": str(self.company1.id),
            "name": "   ",
            "parent_category": None
        }

        url = "/api/categories/"
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"][0], "カテゴリ名は必須です。")

    def test_create_with_too_long_name(self):
        """【異常系】256文字以上のカテゴリ名で作成"""
        data = {
            "company": str(self.company1.id),
            "name": "あ" * 256,  # 256文字
            "parent_category": None
        }

        url = "/api/categories/"
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"][0], "カテゴリ名は255文字以内で入力してください。")

    # カテゴリ名の一意性チェック

    def test_create_with_duplicate_name_in_same_company(self):
        """【異常系】同じ企業内に既に存在するカテゴリ名で作成"""
        data = {
            "company": str(self.company1.id),
            "name": "カテゴリ1",  # 既に存在
            "parent_category": None
        }

        url = "/api/categories/"
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertEqual(response.data["non_field_errors"][0], "この企業には既に同じ名前のカテゴリが存在します。")

    def test_update_with_duplicate_name_in_same_company(self):
        """【異常系】同じ企業内に既に存在するカテゴリ名に更新"""
        # category2の名前をcategory1と同じにしようとする
        data = {
            "company": str(self.company1.id),
            "name": "カテゴリ1",  # category1と重複
            "parent_category": None
        }

        url = f"/api/categories/{self.category2.id}/"
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertEqual(response.data["non_field_errors"][0], "この企業には既に同じ名前のカテゴリが存在します。")

    # 親カテゴリの企業所属チェック

    def test_create_with_parent_from_different_company(self):
        """【異常系】異なる企業のカテゴリを親として指定して作成"""
        data = {
            "company": str(self.company1.id),
            "name": "新規カテゴリ",
            "parent_category": str(self.category3.id)  # company2のカテゴリ
        }

        url = "/api/categories/"
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertEqual(response.data["non_field_errors"][0], "親カテゴリは同じ企業に属している必要があります。")

    def test_update_with_parent_from_different_company(self):
        """【異常系】異なる企業のカテゴリを親として設定して更新"""
        data = {
            "company": str(self.company1.id),
            "name": "カテゴリ1",
            "parent_category": str(self.category3.id)  # company2のカテゴリ
        }

        url = f"/api/categories/{self.category1.id}/"
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertEqual(response.data["non_field_errors"][0], "親カテゴリは同じ企業に属している必要があります。")

    # 自己参照チェック（更新時）

    def test_update_with_self_as_parent(self):
        """【異常系】カテゴリ自身を親カテゴリに設定して更新"""
        data = {
            "company": str(self.company1.id),
            "name": "カテゴリ1",
            "parent_category": str(self.category1.id)  # 自分自身
        }

        url = f"/api/categories/{self.category1.id}/"
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertEqual(response.data["non_field_errors"][0], "カテゴリ自身を親カテゴリに設定することはできません。")

    def test_partial_update_with_self_as_parent(self):
        """【異常系】カテゴリ自身を親カテゴリに設定して部分更新"""
        data = {
            "parent_category": str(self.category1.id)  # 自分自身
        }

        url = f"/api/categories/{self.category1.id}/"
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertEqual(response.data["non_field_errors"][0], "カテゴリ自身を親カテゴリに設定することはできません。")

    # 循環参照チェック（更新時）

    def test_update_with_circular_reference(self):
        """【異常系】循環参照が発生する親カテゴリを設定して更新"""
        # category1 → category2という階層がある
        # category1の親をcategory2に設定すると循環参照になる
        data = {
            "company": str(self.company1.id),
            "name": "カテゴリ1",
            "parent_category": str(self.category2.id)  # 子を親にする
        }

        url = f"/api/categories/{self.category1.id}/"
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertEqual(response.data["non_field_errors"][0], "循環参照が発生するため、この親カテゴリは設定できません。")

    def test_partial_update_with_circular_reference(self):
        """【異常系】循環参照が発生する親カテゴリを設定して部分更新"""
        # 深い階層での循環参照テスト
        # category1 → category2 → category3_new の階層を作成
        category3_new = Category.objects.create(
            company=self.company1,
            name="カテゴリ3_新規",
            parent_category=self.category2
        )

        # category1の親をcategory3_newに設定すると循環参照
        data = {
            "parent_category": str(category3_new.id)
        }

        url = f"/api/categories/{self.category1.id}/"
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertEqual(response.data["non_field_errors"][0], "循環参照が発生するため、この親カテゴリは設定できません。")

    # 404エラーケース

    def test_retrieve_non_existent_category(self):
        """【異常系】存在しないカテゴリの取得"""
        import uuid
        non_existent_id = uuid.uuid4()

        url = f"/api/categories/{non_existent_id}/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_non_existent_category(self):
        """【異常系】存在しないカテゴリの更新"""
        import uuid
        non_existent_id = uuid.uuid4()

        data = {
            "company": str(self.company1.id),
            "name": "更新カテゴリ",
            "parent_category": None
        }

        url = f"/api/categories/{non_existent_id}/"
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_partial_update_non_existent_category(self):
        """【異常系】存在しないカテゴリの部分更新"""
        import uuid
        non_existent_id = uuid.uuid4()

        data = {
            "name": "更新カテゴリ"
        }

        url = f"/api/categories/{non_existent_id}/"
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_destroy_non_existent_category(self):
        """【異常系】存在しないカテゴリの削除"""
        import uuid
        non_existent_id = uuid.uuid4()

        url = f"/api/categories/{non_existent_id}/"
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ========================================
    # 500エラーのテストについて
    # ========================================
    # 500 Internal Server Errorのテストは実装していません。
    #
    # 理由:
    # 1. Django REST Frameworkのユニットテスト環境では、ViewやSerializerで発生した
    #    予期しない例外は自動的に再raiseされ、テストが失敗します。
    #
    # 2. モックを使用して例外を発生させる方法では、DRFの内部エラーハンドリング機構を
    #    バイパスできないため、500エラーレスポンスではなく例外がスローされます。
    #
    # 3. 500エラーは通常、予期しないシステムエラー（データベース接続エラー、
    #    メモリ不足など）によって発生するため、ユニットテストよりも統合テストや
    #    システムテストでカバーすることが適切です。
    #
    # 4. Django/DRFのフレームワーク自体が例外ハンドリングを適切に行っているため、
    #    カスタムエラーハンドリングを実装していない限り、500エラーの動作を
    #    ユニットテストで検証する必要性は低いと判断しました。
