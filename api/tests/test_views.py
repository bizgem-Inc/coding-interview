from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from api.models.category import Category
from api.models.company import Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        # 各テスト共通で使う Company と Category を生成します
        self.company = Company.objects.create(name="テスト用の企業です")
        self.category = Category.objects.create(
            company=self.company,
            name="テスト用の初期カテゴリーです",
            parent_category=None
        )

        print()

    def test_list(self):
        print("\033[96m[TEST] [GET] /api/categories/ で 200 OK & リスト形式で返却されることを確認します\033[0m")

        url = reverse("category-list")
        response = self.client.get(url, format="json")

        # ステータスコードチェック（緑=成功、赤=失敗）
        if response.status_code == status.HTTP_200_OK:
            print("\033[92m[INFO] ステータスコード 200 OK\033[0m")
        else:
            print(f"\033[91m[ERROR] ステータスコード: {response.status_code}\033[0m")

        # レスポンスがリストかチェック
        if isinstance(response.data, list):
            print("\033[92m[INFO] レスポンスデータは list 形式\033[0m")
        else:
            print(f"\033[91m[ERROR] レスポンスデータの型: {type(response.data)}\033[0m")

        # 作成したカテゴリが含まれているか
        returned_ids = [item["id"] for item in response.data]
        if str(self.category.id) in returned_ids:
            print(f"\033[92m[INFO] category.id={self.category.id} がレスポンスに含まれる\033[0m")
        else:
            print(f"\033[91m[ERROR] category.id={self.category.id} がレスポンスに含まれていない\033[0m")


        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertIn(str(self.category.id), returned_ids)

        print()

    def test_retrieve(self):
        print("\033[96m[TEST] [GET] /api/categories/{id}/ で 200 OK & 正しいレコードが返ることを確認します\033[0m")

        url = reverse("category-detail", kwargs={"pk": str(self.category.id)})
        response = self.client.get(url, format="json")

        # ステータスコードチェック
        if response.status_code == status.HTTP_200_OK:
            print("\033[92m[INFO] ステータスコードが 200 OK\033[0m")
        else:
            print(f"\033[91m[ERROR] ステータスコード: {response.status_code}\033[0m")

        # 返ってきた JSON の内容をチェック
        data = response.data

        # id の検証
        if data.get("id") == str(self.category.id):
            print(f"\033[92m[INFO] data['id'] が期待通りです: {data['id']}\033[0m")
        else:
            print(f"\033[91m[ERROR] data['id'] が期待と異なる: {data.get('id')} (期待: {self.category.id})\033[0m")

        # company の検証
        if data.get("company") == self.company.id:
            print(f"\033[92m[INFO] data['company'] が期待通り: {data['company']}\033[0m")
        else:
            print(f"\033[91m[ERROR] data['company'] が期待と異なる: {data.get('company')} (期待: {self.company.id})\033[0m")

        # name の検証
        expected_name = "テスト用の初期カテゴリーです"
        if data.get("name") == expected_name:
            print(f"\033[92m[INFO] data['name'] が期待通り: {data['name']}\033[0m")
        else:
            print(f"\033[91m[ERROR] data['name'] が期待と異なる: {data.get('name')} (期待: {expected_name})\033[0m")

        # parent_category の検証
        if data.get("parent_category") is None:
            print("\033[92m[INFO] data['parent_category'] が None\033[0m")
        else:
            print(f"\033[91m[ERROR] data['parent_category'] が期待と異なる: {data.get('parent_category')} (期待: None)\033[0m")


        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["id"], str(self.category.id))
        self.assertEqual(data["company"], self.company.id)
        self.assertEqual(data["name"], expected_name)
        self.assertIsNone(data["parent_category"])

        print()

    def test_create(self):
        print("\033[96m[TEST] [POST] /api/categories/ で 201 Created & DB にレコードが追加されることを確認します\033[0m")

        url = reverse("category-list")
        payload = {
            "company": str(self.company.id),
            "name": "テスト用の新規カテゴリーです",
            "parent_category": None
        }

        response = self.client.post(url, payload, format="json")

        # ステータスコードチェック
        if response.status_code == status.HTTP_201_CREATED:
            print("\033[92m[INFO] ステータスコードが 201 Created\033[0m")
        else:
            print(f"\033[91m[ERROR] ステータスコード: {response.status_code}\033[0m")

        # DB 上にレコードが存在するかチェック
        exists = Category.objects.filter(
            company=self.company,
            name="テスト用の新規カテゴリーです"
        ).exists()
        if exists:
            print("\033[92m[INFO] DB に同名レコードが追加されている\033[0m")
        else:
            print("\033[91m[ERROR] DB に同名レコードが存在しない\033[0m")

        # 返ってきた JSON の内容をチェック
        data = response.data

        # company フィールド検証
        if data.get("company") == self.company.id:
            print(f"\033[92m[INFO] data['company'] が期待通り: {data['company']}\033[0m")
        else:
            print(f"\033[91m[ERROR] data['company'] が期待と異なる: {data.get('company')} (期待: {self.company.id})\033[0m")

        # name フィールド検証
        expected_name = "テスト用の新規カテゴリーです"
        if data.get("name") == expected_name:
            print(f"\033[92m[INFO] data['name'] が期待通り: {data['name']}\033[0m")
        else:
            print(f"\033[91m[ERROR] data['name'] が期待と異なる: {data.get('name')} (期待: {expected_name})\033[0m")

        # parent_category フィールド検証
        if data.get("parent_category") is None:
            print("\033[92m[INFO] data['parent_category'] が None\033[0m")
        else:
            print(f"\033[91m[ERROR] data['parent_category'] が期待と異なる: {data.get('parent_category')} (期待: None)\033[0m")


        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exists)
        self.assertEqual(data["company"], self.company.id)
        self.assertEqual(data["name"], expected_name)
        self.assertIsNone(data["parent_category"])

        print()

    def test_updata(self):
        print("\033[96m[TEST] [PUT] /api/categories/{id}/ で 200 OK & レコードが更新されることを確認します\033[0m")

        url = reverse("category-detail", kwargs={"pk": str(self.category.id)})
        payload = {
            "company": str(self.company.id),
            "name": "テスト用に更新されたカテゴリです",
            "parent_category": None
        }

        response = self.client.put(url, payload, format="json")

        # ステータスコードチェック
        if response.status_code == status.HTTP_200_OK:
            print("\033[92m[INFO] ステータスコードが 200 OK\033[0m")
        else:
            print(f"\033[91m[ERROR] ステータスコード: {response.status_code}\033[0m")

        # DB 上で name が更新されているかチェック
        self.category.refresh_from_db()
        updated_name = self.category.name
        expected_name = "テスト用に更新されたカテゴリです"
        if updated_name == expected_name:
            print(f"\033[92m[INFO] DB 上の name が期待通りに更新されている: {updated_name}\033[0m")
        else:
            print(f"\033[91m[ERROR] DB 上の name が期待と異なる: {updated_name} (期待: {expected_name})\033[0m")

        # レスポンスの JSON にも更新後の name が含まれているかチェック
        data = response.data
        if data.get("name") == expected_name:
            print(f"\033[92m[INFO] response.data['name'] が期待通り: {data['name']}\033[0m")
        else:
            print(f"\033[91m[ERROR] response.data['name'] が期待と異なる: {data.get('name')} (期待: {expected_name})\033[0m")


        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.category.name, expected_name)
        self.assertEqual(data["name"], expected_name)

        print()

    def test_destroy(self):
        print("\033[96m[TEST] [DELETE] /api/categories/{id}/ で 204 No Content & レコードが削除されることを確認します\033[0m")

        url = reverse("category-detail", kwargs={"pk": str(self.category.id)})
        response = self.client.delete(url, format="json")

        # ステータスコードチェック
        if response.status_code == status.HTTP_204_NO_CONTENT:
            print("\033[92m[OK] ステータスコードが 204 No Content\033[0m")
        else:
            print(f"\033[91m[NG] ステータスコード: {response.status_code}\033[0m")

        # DB 上に該当レコードが存在しないかチェック
        still_exists = Category.objects.filter(pk=self.category.id).exists()
        if not still_exists:
            print(f"\033[92m[OK] DB に id={self.category.id} のレコードが存在しない\033[0m")
        else:
            print(f"\033[91m[NG] DB に id={self.category.id} のレコードがまだ存在する\033[0m")


        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(still_exists)
