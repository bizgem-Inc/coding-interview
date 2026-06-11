import uuid

from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from api.repositories.django.orm_models.company import CompanyModel as Company

# 静的ファイル設定をテスト時に無効化
STATIC_URL = "static/"


@override_settings(STATICFILES_DIRS=[])
class CategoryViewTests(APITestCase):
    """Category CRUD APIの統合テスト。

    テスト対象:
    - HTTP契約: ステータスコード、レスポンス項目
    - 入力検証: UUID形式、必須項目、文字数上限
    - 参照整合性: Company、親Categoryの存在確認
    - 一意制約: 同一Company内の名前重複
    - トランザクション: 失敗時のロールバック
    """

    def setUp(self):
        self.company = Company.objects.create(name="TestCorp")

    # ------------------------------------------------------------------
    # 一覧取得
    # ------------------------------------------------------------------

    def test_list(self):
        """Category一覧が200で返る。"""
        response = self.client.get("/api/categories/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsInstance(data, list)

    def test_list_with_pagination(self):
        """limitとpageでページネーションが機能する。"""
        for name in ("A", "B", "C", "D", "E"):
            self.client.post(
                "/api/categories/",
                {"company_id": str(self.company.id), "name": name},
                format="json",
            )
        response = self.client.get("/api/categories/?limit=2&page=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)

        response = self.client.get("/api/categories/?limit=2&page=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)

        response = self.client.get("/api/categories/?limit=2&page=3")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_list_limit_capped_at_100(self):
        """limitが100を超えると100に制限される。"""
        for name in ("A", "B", "C"):
            self.client.post(
                "/api/categories/",
                {"company_id": str(self.company.id), "name": name},
                format="json",
            )
        response = self.client.get("/api/categories/?limit=200")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 3)

    def test_list_invalid_params_uses_defaults(self):
        """不正なlimit/pageパラメータではデフォルト値(limit=10, page=1)が適用される。"""
        self.client.post(
            "/api/categories/",
            {"company_id": str(self.company.id), "name": "Test"},
            format="json",
        )
        response = self.client.get("/api/categories/?limit=abc&page=xyz")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_list_default_limit(self):
        """limitパラメータなしでデフォルト10件が適用される。"""
        for name in range(15):
            self.client.post(
                "/api/categories/",
                {"company_id": str(self.company.id), "name": str(name)},
                format="json",
            )
        response = self.client.get("/api/categories/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 10)

    def test_list_page_capped_at_1m(self):
        """pageが100万を超えると100万に制限される。"""
        response = self.client.get("/api/categories/?page=9999999")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 0)

    def test_list_returns_json_for_browser_request(self):
        """ブラウザからのアクセスでもBrowsable APIではなくJSONを返す。"""
        response = self.client.get(
            "/api/categories/",
            HTTP_ACCEPT="text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertIsInstance(response.json(), list)

    def test_list_includes_all_fields(self):
        """一覧レスポンスに全フィールドが含まれる。"""
        # Categoryを作成してから一覧を取得
        create_resp = self.client.post(
            "/api/categories/",
            {"company_id": str(self.company.id), "name": "Backend"},
            format="json",
        )
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        response = self.client.get("/api/categories/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 1)
        item = data[0]
        for field in ["id", "company_id", "name", "parent_category_id", "created_at", "updated_at"]:
            self.assertIn(field, item)

    # ------------------------------------------------------------------
    # 詳細取得
    # ------------------------------------------------------------------

    def test_retrieve(self):
        """存在するCategoryの詳細が200で返る。"""
        create_resp = self.client.post(
            "/api/categories/",
            {"company_id": str(self.company.id), "name": "Backend"},
            format="json",
        )
        category_id = create_resp.json()["id"]
        response = self.client.get(f"/api/categories/{category_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["name"], "Backend")
        self.assertEqual(data["id"], category_id)

    def test_retrieve_missing_returns_404(self):
        """存在しないCategoryの詳細取得が404を返す。"""
        response = self.client.get(f"/api/categories/{uuid.uuid4()}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_invalid_uuid_returns_400(self):
        """不正なUUID形式が400を返す。"""
        response = self.client.get("/api/categories/not-a-uuid/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------
    # 作成
    # ------------------------------------------------------------------

    def test_create(self):
        """Categoryが作成できる。"""
        payload = {
            "company_id": str(self.company.id),
            "name": "Backend",
            "parent_category_id": None,
        }
        response = self.client.post("/api/categories/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data["name"], "Backend")
        self.assertEqual(data["company_id"], str(self.company.id))
        self.assertEqual(data["parent_category_id"], None)
        self.assertIn("id", data)
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)

    def test_create_with_parent(self):
        """親Categoryを指定して作成できる。"""
        parent_resp = self.client.post(
            "/api/categories/",
            {"company_id": str(self.company.id), "name": "Engineering"},
            format="json",
        )
        parent_id = parent_resp.json()["id"]
        payload = {
            "company_id": str(self.company.id),
            "name": "Backend",
            "parent_category_id": parent_id,
        }
        response = self.client.post("/api/categories/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data["parent_category_id"], parent_id)

    def test_create_missing_company_returns_400(self):
        """存在しないCompanyを指定すると400が返る。"""
        payload = {
            "company_id": str(uuid.uuid4()),
            "name": "Backend",
            "parent_category_id": None,
        }
        response = self.client.post("/api/categories/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_missing_parent_returns_400(self):
        """存在しない親Categoryを指定すると400が返る。"""
        payload = {
            "company_id": str(self.company.id),
            "name": "Backend",
            "parent_category_id": str(uuid.uuid4()),
        }
        response = self.client.post("/api/categories/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_missing_name_returns_400(self):
        """nameが不足していると400が返る。"""
        payload = {
            "company_id": str(self.company.id),
        }
        response = self.client.post("/api/categories/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_missing_company_id_returns_400(self):
        """company_idが不足していると400が返る。"""
        payload = {
            "name": "Backend",
        }
        response = self.client.post("/api/categories/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_company_id_returns_400(self):
        """不正なcompany_id形式が400を返す。"""
        payload = {
            "company_id": "not-a-uuid",
            "name": "Backend",
        }
        response = self.client.post("/api/categories/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_name_too_long_returns_400(self):
        """nameが255文字を超える場合400が返る。"""
        payload = {
            "company_id": str(self.company.id),
            "name": "A" * 256,
        }
        response = self.client.post("/api/categories/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_name_in_company_returns_400(self):
        """同一Company内で重複する名前が400を返す。"""
        self.client.post(
            "/api/categories/",
            {"company_id": str(self.company.id), "name": "Backend"},
            format="json",
        )
        response = self.client.post(
            "/api/categories/",
            {"company_id": str(self.company.id), "name": "Backend"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------
    # 更新 (PUT)
    # ------------------------------------------------------------------

    def test_update(self):
        """CategoryがPUTで更新できる。"""
        create_resp = self.client.post(
            "/api/categories/",
            {"company_id": str(self.company.id), "name": "Backend"},
            format="json",
        )
        category_id = create_resp.json()["id"]
        payload = {
            "company_id": str(self.company.id),
            "name": "Backend Updated",
            "parent_category_id": None,
        }
        response = self.client.put(f"/api/categories/{category_id}/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["name"], "Backend Updated")

    def test_update_missing_returns_404(self):
        """存在しないCategoryの更新が404を返す。"""
        payload = {
            "company_id": str(self.company.id),
            "name": "Updated",
            "parent_category_id": None,
        }
        response = self.client.put(f"/api/categories/{uuid.uuid4()}/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_missing_company_returns_400(self):
        """存在しないCompanyを指定した更新が400を返す。"""
        create_resp = self.client.post(
            "/api/categories/",
            {"company_id": str(self.company.id), "name": "Backend"},
            format="json",
        )
        category_id = create_resp.json()["id"]
        payload = {
            "company_id": str(uuid.uuid4()),
            "name": "Updated",
            "parent_category_id": None,
        }
        response = self.client.put(f"/api/categories/{category_id}/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_missing_parent_returns_400(self):
        """存在しない親Categoryを指定した更新が400を返す（404ではない）。"""
        create_resp = self.client.post(
            "/api/categories/",
            {"company_id": str(self.company.id), "name": "Backend"},
            format="json",
        )
        category_id = create_resp.json()["id"]
        payload = {
            "company_id": str(self.company.id),
            "name": "Backend",
            "parent_category_id": str(uuid.uuid4()),
        }
        response = self.client.put(f"/api/categories/{category_id}/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------
    # 部分的更新 (PATCH)
    # ------------------------------------------------------------------

    def test_partial_update(self):
        """CategoryがPATCHで部分的に更新できる。"""
        create_resp = self.client.post(
            "/api/categories/",
            {"company_id": str(self.company.id), "name": "Backend"},
            format="json",
        )
        category_id = create_resp.json()["id"]
        response = self.client.patch(
            f"/api/categories/{category_id}/",
            {"name": "PATCH Updated"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["name"], "PATCH Updated")

    def test_partial_update_missing_returns_404(self):
        """存在しないCategoryのPATCHが404を返す。"""
        payload = {"name": "Updated"}
        response = self.client.patch(f"/api/categories/{uuid.uuid4()}/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_partial_update_null_name_returns_400(self):
        """PATCHでnameにnullを指定すると400が返る。"""
        create_resp = self.client.post(
            "/api/categories/",
            {"company_id": str(self.company.id), "name": "Backend"},
            format="json",
        )
        category_id = create_resp.json()["id"]
        response = self.client.patch(
            f"/api/categories/{category_id}/",
            {"name": None},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_update_null_company_id_returns_400(self):
        """PATCHでcompany_idにnullを指定すると400が返る。"""
        create_resp = self.client.post(
            "/api/categories/",
            {"company_id": str(self.company.id), "name": "Backend"},
            format="json",
        )
        category_id = create_resp.json()["id"]
        response = self.client.patch(
            f"/api/categories/{category_id}/",
            {"company_id": None},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_update_missing_parent_returns_400(self):
        """PATCHで存在しない親Categoryを指定すると400が返る。"""
        create_resp = self.client.post(
            "/api/categories/",
            {"company_id": str(self.company.id), "name": "Backend"},
            format="json",
        )
        category_id = create_resp.json()["id"]
        response = self.client.patch(
            f"/api/categories/{category_id}/",
            {"parent_category_id": str(uuid.uuid4())},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------
    # 削除
    # ------------------------------------------------------------------

    def test_destroy(self):
        """Categoryが削除できる。"""
        create_resp = self.client.post(
            "/api/categories/",
            {"company_id": str(self.company.id), "name": "Backend"},
            format="json",
        )
        category_id = create_resp.json()["id"]
        response = self.client.delete(f"/api/categories/{category_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # 削除後に404が返ることを確認
        response = self.client.get(f"/api/categories/{category_id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_destroy_missing_returns_404(self):
        """存在しないCategoryの削除が404を返す。"""
        response = self.client.delete(f"/api/categories/{uuid.uuid4()}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ------------------------------------------------------------------
    # トランザクション
    # ------------------------------------------------------------------

    def test_write_rolls_back_when_use_case_fails(self):
        """Use Case失敗時に全更新がロールバックされる。"""
        # 重複名作成で失敗し、DB状態が変化しないことを確認
        self.client.post(
            "/api/categories/",
            {"company_id": str(self.company.id), "name": "Backend"},
            format="json",
        )
        # 重複名での作成は失敗する
        response = self.client.post(
            "/api/categories/",
            {"company_id": str(self.company.id), "name": "Backend"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # 既存のCategoryは1件のみであることを確認
        list_resp = self.client.get("/api/categories/")
        self.assertEqual(len(list_resp.json()), 1)
