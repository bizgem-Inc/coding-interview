import uuid

import pytest


class TestCategoryCrud:
    """live_server上でのCategory CRUD全フローを検証する。"""

    # ------------------------------------------------------------------
    # 一覧取得
    # ------------------------------------------------------------------

    def test_list(self, client, company):  # type: ignore[no-untyped-def]
        """一覧取得が200を返し、配列が返る。"""
        response = client.get("/api/categories/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_with_pagination(self, client, company):  # type: ignore[no-untyped-def]
        """limitとpageでページネーションが機能する。"""
        for name in ("A", "B", "C", "D", "E"):
            client.post(
                "/api/categories/",
                json={"company_id": str(company.id), "name": name, "parent_category_id": None},
            )
        resp = client.get("/api/categories/?limit=2&page=1")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

        resp = client.get("/api/categories/?limit=2&page=2")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

        resp = client.get("/api/categories/?limit=2&page=3")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_limit_capped_at_100(self, client, company):  # type: ignore[no-untyped-def]
        """limitが100を超えると100に制限される。"""
        for name in ("A", "B", "C"):
            client.post(
                "/api/categories/",
                json={"company_id": str(company.id), "name": name, "parent_category_id": None},
            )
        resp = client.get("/api/categories/?limit=200")
        assert resp.status_code == 200
        assert len(resp.json()) == 3

    def test_list_invalid_params_uses_defaults(self, client, company):  # type: ignore[no-untyped-def]
        """不正なlimit/pageパラメータではデフォルト値(limit=10, page=1)が適用される。"""
        client.post(
            "/api/categories/",
            json={"company_id": str(company.id), "name": "Test", "parent_category_id": None},
        )
        resp = client.get("/api/categories/?limit=abc&page=xyz")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_default_limit(self, client, company):  # type: ignore[no-untyped-def]
        """limitパラメータなしでデフォルト10件が適用される。"""
        for name in range(15):
            client.post(
                "/api/categories/",
                json={"company_id": str(company.id), "name": str(name), "parent_category_id": None},
            )
        resp = client.get("/api/categories/")
        assert resp.status_code == 200
        assert len(resp.json()) == 10

    def test_list_page_capped_at_1m(self, client, company):  # type: ignore[no-untyped-def]
        """pageが100万を超えると100万に制限される。"""
        resp = client.get("/api/categories/?page=9999999")
        assert resp.status_code == 200
        assert len(resp.json()) == 0

    # ------------------------------------------------------------------
    # 作成
    # ------------------------------------------------------------------

    def test_create(self, client, company):  # type: ignore[no-untyped-def]
        """作成が201を返し、全フィールドが含まれる。"""
        payload = {
            "company_id": str(company.id),
            "name": "Backend",
            "parent_category_id": None,
        }
        response = client.post("/api/categories/", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["company_id"] == str(company.id)
        assert data["name"] == "Backend"
        assert data["parent_category_id"] is None
        assert "created_at" in data
        assert "updated_at" in data

    def test_retrieve_after_create(self, client, company):  # type: ignore[no-untyped-def]
        """作成直後に詳細取得で同一データが返る。"""
        payload = {
            "company_id": str(company.id),
            "name": "Frontend",
            "parent_category_id": None,
        }
        create_resp = client.post("/api/categories/", json=payload)
        category_id = create_resp.json()["id"]

        response = client.get(f"/api/categories/{category_id}/")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == category_id
        assert data["name"] == "Frontend"

    # ------------------------------------------------------------------
    # 更新 (PUT)
    # ------------------------------------------------------------------

    def test_update(self, client, company):  # type: ignore[no-untyped-def]
        """PUT更新が200を返し、全フィールドが含まれる。"""
        payload = {
            "company_id": str(company.id),
            "name": "ToUpdate",
            "parent_category_id": None,
        }
        create_resp = client.post("/api/categories/", json=payload)
        category_id = create_resp.json()["id"]

        update_payload = {
            "company_id": str(company.id),
            "name": "Updated",
            "parent_category_id": None,
        }
        response = client.put(f"/api/categories/{category_id}/", json=update_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == category_id
        assert data["name"] == "Updated"
        assert "company_id" in data
        assert "parent_category_id" in data
        assert "created_at" in data
        assert "updated_at" in data

    # ------------------------------------------------------------------
    # 部分的更新 (PATCH)
    # ------------------------------------------------------------------

    def test_partial_update(self, client, company):  # type: ignore[no-untyped-def]
        """PATCH部分更新が200を返し、更新後永続化が確認できる。"""
        payload = {
            "company_id": str(company.id),
            "name": "Original",
            "parent_category_id": None,
        }
        create_resp = client.post("/api/categories/", json=payload)
        category_id = create_resp.json()["id"]

        response = client.patch(f"/api/categories/{category_id}/", json={"name": "Patched"})
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Patched"

        # 永続化を確認
        retrieve_resp = client.get(f"/api/categories/{category_id}/")
        assert retrieve_resp.json()["name"] == "Patched"

    # ------------------------------------------------------------------
    # 削除
    # ------------------------------------------------------------------

    def test_destroy(self, client, company):  # type: ignore[no-untyped-def]
        """削除が204を返し、その後404になる。"""
        payload = {
            "company_id": str(company.id),
            "name": "ToDelete",
            "parent_category_id": None,
        }
        create_resp = client.post("/api/categories/", json=payload)
        category_id = create_resp.json()["id"]

        response = client.delete(f"/api/categories/{category_id}/")
        assert response.status_code == 204

        # 削除後に404
        retrieve_resp = client.get(f"/api/categories/{category_id}/")
        assert retrieve_resp.status_code == 404

    # ------------------------------------------------------------------
    # 404
    # ------------------------------------------------------------------

    def test_missing_returns_404(self, client):  # type: ignore[no-untyped-def]
        """存在しないリソースが404を返す。"""
        response = client.get(f"/api/categories/{uuid.uuid4()}/")
        assert response.status_code == 404

    # ------------------------------------------------------------------
    # 入力検証
    # ------------------------------------------------------------------

    def test_create_missing_name(self, client, company):  # type: ignore[no-untyped-def]
        """必須項目nameが不足すると400。"""
        payload = {"company_id": str(company.id)}
        response = client.post("/api/categories/", json=payload)
        assert response.status_code == 400

    def test_create_invalid_uuid(self, client, company):  # type: ignore[no-untyped-def]
        """不正UUIDで400。"""
        payload = {
            "company_id": "not-a-uuid",
            "name": "Test",
        }
        response = client.post("/api/categories/", json=payload)
        assert response.status_code == 400

    def test_create_name_too_long(self, client, company):  # type: ignore[no-untyped-def]
        """255文字超の名前で400。"""
        payload = {
            "company_id": str(company.id),
            "name": "A" * 256,
        }
        response = client.post("/api/categories/", json=payload)
        assert response.status_code == 400

    def test_create_null_company_id(self, client, company):  # type: ignore[no-untyped-def]
        """company_idがnullで400。"""
        payload = {
            "company_id": None,
            "name": "Test",
        }
        response = client.post("/api/categories/", json=payload)
        assert response.status_code == 400

    # ------------------------------------------------------------------
    # 参照整合性
    # ------------------------------------------------------------------

    def test_create_missing_company(self, client, company):  # type: ignore[no-untyped-def]
        """存在しないCompanyで400。"""
        payload = {
            "company_id": str(uuid.uuid4()),
            "name": "Test",
        }
        response = client.post("/api/categories/", json=payload)
        assert response.status_code == 400

    def test_create_missing_parent(self, client, company):  # type: ignore[no-untyped-def]
        """存在しない親Categoryで400。"""
        payload = {
            "company_id": str(company.id),
            "name": "Test",
            "parent_category_id": str(uuid.uuid4()),
        }
        response = client.post("/api/categories/", json=payload)
        assert response.status_code == 400

    # ------------------------------------------------------------------
    # PATCHの明示的null
    # ------------------------------------------------------------------

    def test_patch_null_name(self, client, company):  # type: ignore[no-untyped-def]
        """PATCHでnameにnullを指定すると400。"""
        payload = {
            "company_id": str(company.id),
            "name": "Original",
            "parent_category_id": None,
        }
        create_resp = client.post("/api/categories/", json=payload)
        category_id = create_resp.json()["id"]

        response = client.patch(f"/api/categories/{category_id}/", json={"name": None})
        assert response.status_code == 400

    def test_patch_null_company_id(self, client, company):  # type: ignore[no-untyped-def]
        """PATCHでcompany_idにnullを指定すると400。"""
        payload = {
            "company_id": str(company.id),
            "name": "Original",
            "parent_category_id": None,
        }
        create_resp = client.post("/api/categories/", json=payload)
        category_id = create_resp.json()["id"]

        response = client.patch(f"/api/categories/{category_id}/", json={"company_id": None})
        assert response.status_code == 400
