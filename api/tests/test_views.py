import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier

import psycopg2
from django.db import connections
from django.db.models.signals import pre_save
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase, APITransactionTestCase

from api.models import Category, Company


class CategoryViewTests(APITestCase):
    """Category APIのCRUDと入力バリデーションをPostgreSQL上で確認する。"""

    def setUp(self):
        # 各テストが同じ前提で独立して動くよう、企業を1件用意する。
        self.company = Company.objects.create(name="Bizgem")
        self.list_url = reverse("category-list")

    @staticmethod
    def detail_url(category_id):
        # 指定したCategory IDから詳細APIのURLを生成する。
        return reverse("category-detail", kwargs={"pk": category_id})

    def assert_category_response(self, response, category):
        # Categoryレスポンスの項目と各値がDB上の状態に一致することを確認する。
        data = response.json()
        self.assertEqual(
            set(data),
            {"id", "company", "name", "parent_category", "created_at", "updated_at"},
        )
        self.assertEqual(data["id"], str(category.id))
        self.assertEqual(data["company"], str(category.company_id))
        self.assertEqual(data["name"], category.name)
        self.assertEqual(
            data["parent_category"],
            str(category.parent_category_id) if category.parent_category_id else None,
        )
        self.assertIsNotNone(data["created_at"])
        self.assertIsNotNone(data["updated_at"])

    def test_list_returns_categories_in_queryset_order(self):
        # 作成順・名前順と異なるcreated_at順で一覧が返ることを確認する。
        newer = Category.objects.create(company=self.company, name="Alpha")
        older = Category.objects.create(company=self.company, name="Zulu")
        base_time = timezone.now()
        Category.objects.filter(id=older.id).update(created_at=base_time)
        Category.objects.filter(id=newer.id).update(
            created_at=base_time + timedelta(seconds=1)
        )

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [item["id"] for item in response.json()],
            [str(older.id), str(newer.id)],
        )

    def test_retrieve_returns_complete_category_response(self):
        # 指定したCategoryの詳細と全レスポンス項目を取得できることを確認する。
        category = Category.objects.create(company=self.company, name="Backend")

        response = self.client.get(self.detail_url(category.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_category_response(response, category)

    def test_create_returns_created_category_and_persists_it(self):
        # 必須項目を送信して親なしCategoryを作成できることを確認する。
        response = self.client.post(
            self.list_url,
            {"company": str(self.company.id), "name": "Backend"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        category = Category.objects.get(id=response.json()["id"])
        self.assertEqual(category.company, self.company)
        self.assertEqual(category.name, "Backend")
        self.assertIsNone(category.parent_category)
        self.assert_category_response(response, category)

    def test_create_with_parent_returns_created_child(self):
        # 親Categoryを指定して子Categoryを作成できることを確認する。
        parent = Category.objects.create(company=self.company, name="Engineering")

        response = self.client.post(
            self.list_url,
            {
                "company": str(self.company.id),
                "name": "Backend",
                "parent_category": str(parent.id),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        category = Category.objects.get(id=response.json()["id"])
        self.assertEqual(category.parent_category, parent)
        self.assert_category_response(response, category)

    def test_put_returns_updated_category_and_persists_changes(self):
        # PUTでCategoryの名前と親Categoryを更新できることを確認する。
        category = Category.objects.create(company=self.company, name="Backend")
        parent = Category.objects.create(company=self.company, name="Engineering")

        response = self.client.put(
            self.detail_url(category.id),
            {
                "company": str(self.company.id),
                "name": "Platform",
                "parent_category": str(parent.id),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        category.refresh_from_db()
        self.assertEqual(category.name, "Platform")
        self.assertEqual(category.parent_category, parent)
        self.assert_category_response(response, category)

    def test_patch_returns_updated_category_and_preserves_omitted_fields(self):
        # PATCHで指定項目だけを更新し、未指定項目が維持されることを確認する。
        category = Category.objects.create(company=self.company, name="Backend")

        response = self.client.patch(
            self.detail_url(category.id),
            {"name": "Platform"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        category.refresh_from_db()
        self.assertEqual(category.name, "Platform")
        self.assertEqual(category.company, self.company)
        self.assert_category_response(response, category)

    def test_delete_returns_204_and_removes_category(self):
        # DELETEでCategoryがデータベースから削除されることを確認する。
        category = Category.objects.create(company=self.company, name="Backend")

        response = self.client.delete(self.detail_url(category.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=category.id).exists())

    def test_delete_parent_sets_child_parent_to_null(self):
        # 親Categoryの削除後も子を残し、親参照がnullになることを確認する。
        parent = Category.objects.create(company=self.company, name="Engineering")
        child = Category.objects.create(
            company=self.company,
            name="Backend",
            parent_category=parent,
        )

        response = self.client.delete(self.detail_url(parent.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        child.refresh_from_db()
        self.assertIsNone(child.parent_category)

    def test_retrieve_unknown_id_returns_404(self):
        # UUID形式は正しいが存在しないIDへの詳細取得が404になることを確認する。
        response = self.client.get(self.detail_url(uuid.uuid4()))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_malformed_id_returns_404(self):
        # UUID形式でないIDへの詳細取得が404になることを確認する。
        response = self.client.get("/api/categories/not-a-uuid/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_without_required_fields_returns_400(self):
        # companyまたはnameが不足した作成リクエストが400になることを確認する。
        invalid_payloads = (
            ({"name": "Backend"}, "company"),
            ({"company": str(self.company.id)}, "name"),
        )

        for payload, missing_field in invalid_payloads:
            with self.subTest(missing_field=missing_field):
                response = self.client.post(self.list_url, payload, format="json")

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(missing_field, response.json())

    def test_create_blank_name_returns_400(self):
        # 空文字または空白だけのnameが400になることを確認する。
        for name in ("", "   "):
            with self.subTest(name=name):
                response = self.client.post(
                    self.list_url,
                    {"company": str(self.company.id), "name": name},
                    format="json",
                )

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn("name", response.json())

    def test_create_name_over_max_length_returns_400(self):
        # 最大長255文字を超えるnameが400になることを確認する。
        response = self.client.post(
            self.list_url,
            {"company": str(self.company.id), "name": "a" * 256},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.json())

    def test_create_name_at_max_length_returns_201(self):
        # 最大長ちょうど255文字のnameを登録できることを確認する。
        response = self.client.post(
            self.list_url,
            {"company": str(self.company.id), "name": "a" * 255},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_malformed_company_uuid_returns_400(self):
        # UUID形式でないcompanyを指定した作成リクエストが400になることを確認する。
        response = self.client.post(
            self.list_url,
            {"company": "not-a-uuid", "name": "Backend"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("company", response.json())

    def test_create_unknown_company_returns_400(self):
        # UUID形式は正しいが存在しないcompanyを指定すると400になることを確認する。
        response = self.client.post(
            self.list_url,
            {"company": str(uuid.uuid4()), "name": "Backend"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("company", response.json())

    def test_create_unknown_parent_category_returns_400(self):
        # 存在しない親Categoryを指定した作成リクエストが400になることを確認する。
        response = self.client.post(
            self.list_url,
            {
                "company": str(self.company.id),
                "name": "Backend",
                "parent_category": str(uuid.uuid4()),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.json())

    def test_create_parent_from_different_company_returns_400(self):
        # 作成先と異なる企業のCategoryを親に指定すると400になることを確認する。
        other_company = Company.objects.create(name="Other")
        parent = Category.objects.create(company=other_company, name="Engineering")

        response = self.client.post(
            self.list_url,
            {
                "company": str(self.company.id),
                "name": "Backend",
                "parent_category": str(parent.id),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.json())

    def test_patch_self_as_parent_returns_400(self):
        # Category自身を親に指定するPATCHが400になることを確認する。
        category = Category.objects.create(company=self.company, name="Backend")

        response = self.client.patch(
            self.detail_url(category.id),
            {"parent_category": str(category.id)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.json())
        category.refresh_from_db()
        self.assertIsNone(category.parent_category)

    def test_patch_parent_that_creates_cycle_returns_400(self):
        # 子Categoryを親に設定して循環参照を作るPATCHが400になることを確認する。
        parent = Category.objects.create(company=self.company, name="Engineering")
        child = Category.objects.create(
            company=self.company,
            name="Backend",
            parent_category=parent,
        )

        response = self.client.patch(
            self.detail_url(parent.id),
            {"parent_category": str(child.id)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.json())
        parent.refresh_from_db()
        self.assertIsNone(parent.parent_category)

    def test_patch_company_conflicting_with_parent_returns_400(self):
        # 親と異なる企業へ子Categoryを変更するPATCHが400になることを確認する。
        parent = Category.objects.create(company=self.company, name="Engineering")
        category = Category.objects.create(
            company=self.company,
            name="Backend",
            parent_category=parent,
        )
        other_company = Company.objects.create(name="Other")

        response = self.client.patch(
            self.detail_url(category.id),
            {"company": str(other_company.id)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.json())
        category.refresh_from_db()
        self.assertEqual(category.company, self.company)

    def test_patch_company_conflicting_with_child_returns_400(self):
        # 子と異なる企業へ親Categoryを変更するPATCHが400になることを確認する。
        category = Category.objects.create(company=self.company, name="Engineering")
        Category.objects.create(
            company=self.company,
            name="Backend",
            parent_category=category,
        )
        other_company = Company.objects.create(name="Other")

        response = self.client.patch(
            self.detail_url(category.id),
            {"company": str(other_company.id)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("company", response.json())
        category.refresh_from_db()
        self.assertEqual(category.company, self.company)

    def test_patch_company_without_relations_returns_updated_category(self):
        # 親子関係がなければ企業を変更でき、更新後の内容が返ることを確認する。
        category = Category.objects.create(company=self.company, name="Backend")
        other_company = Company.objects.create(name="Other")

        response = self.client.patch(
            self.detail_url(category.id),
            {"company": str(other_company.id)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        category.refresh_from_db()
        self.assertEqual(category.company, other_company)
        self.assert_category_response(response, category)

    def test_create_duplicate_company_and_name_returns_400(self):
        # 同じcompanyとnameのCategoryを重複作成できないことを確認する。
        Category.objects.create(company=self.company, name="Backend")

        response = self.client.post(
            self.list_url,
            {"company": str(self.company.id), "name": "Backend"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.json())
        self.assertEqual(
            Category.objects.filter(company=self.company, name="Backend").count(),
            1,
        )

    def test_create_same_name_for_different_companies_returns_201(self):
        # companyが異なれば同じnameのCategoryを作成できることを確認する。
        Category.objects.create(company=self.company, name="Backend")
        other_company = Company.objects.create(name="Other")

        response = self.client.post(
            self.list_url,
            {"company": str(other_company.id), "name": "Backend"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_duplicate_company_and_name_returns_400(self):
        # 更新によってcompanyとnameの重複が発生する場合は400になることを確認する。
        Category.objects.create(company=self.company, name="Backend")
        category = Category.objects.create(company=self.company, name="Frontend")

        response = self.client.patch(
            self.detail_url(category.id),
            {"name": "Backend"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.json())
        category.refresh_from_db()
        self.assertEqual(category.name, "Frontend")

class CategoryConcurrentRequestTests(APITransactionTestCase):
    """公開APIへの同時リクエストでもデータ整合性を保てることを確認する。"""

    def setUp(self):
        # 並行スレッドから参照できるよう、トランザクション外で企業を作成する。
        self.company = Company.objects.create(name="Bizgem")
        self.list_url = reverse("category-list")

    @staticmethod
    def detail_url(category_id):
        # 指定したCategory IDから詳細APIのURLを生成する。
        return reverse("category-detail", kwargs={"pk": category_id})

    @staticmethod
    def open_control_connection():
        # 競合状態を作るため、Djangoとは別のPostgreSQL接続を開始する。
        database = connections["default"].settings_dict
        return psycopg2.connect(
            dbname=database["NAME"],
            user=database["USER"],
            password=database["PASSWORD"],
            host=database["HOST"],
            port=database["PORT"],
            application_name="category-api-race-test",
        )

    def wait_for_blocked_queries(
        self,
        control_connection,
        query_fragment,
        expected_count,
    ):
        # API処理が指定SQLのロック待ちへ到達するまで待機する。
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            with control_connection.cursor() as cursor:
                cursor.execute("SELECT pg_stat_clear_snapshot()")
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM pg_stat_activity
                    WHERE datname = current_database()
                      AND pid <> pg_backend_pid()
                      AND wait_event_type = 'Lock'
                      AND query ILIKE %s
                    """,
                    (f"%{query_fragment}%",),
                )
                if cursor.fetchone()[0] >= expected_count:
                    return
            time.sleep(0.05)
        self.fail(
            f"{query_fragment!r} のロック待ちが{expected_count}件に達しませんでした。"
        )

    def post_duplicate_category(self):
        # スレッド専用DB接続とAPIClientで同じCategoryをPOSTする。
        connections.close_all()
        try:
            response = APIClient().post(
                self.list_url,
                {"company": str(self.company.id), "name": "Backend"},
                format="json",
            )
            return response.status_code, response.json()
        finally:
            connections.close_all()

    def test_concurrent_duplicate_posts_return_201_and_400(self):
        # 両POSTを検証後・INSERT直前で同期し、DB一意制約の競合応答を確認する。
        insert_barrier = Barrier(2)

        def wait_immediately_before_insert(sender, instance, **kwargs):
            # 対象CategoryのINSERT直前で2リクエストを合流させる。
            if instance._state.adding and instance.name == "Backend":
                insert_barrier.wait(timeout=10)

        dispatch_uid = "category-api-concurrent-duplicate-insert"
        pre_save.connect(
            wait_immediately_before_insert,
            sender=Category,
            dispatch_uid=dispatch_uid,
            weak=False,
        )
        try:
            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = [
                    executor.submit(self.post_duplicate_category) for _ in range(2)
                ]
                results = [future.result(timeout=15) for future in futures]
        finally:
            pre_save.disconnect(sender=Category, dispatch_uid=dispatch_uid)

        self.assertEqual(sorted(result[0] for result in results), [201, 400])
        conflict_body = next(body for code, body in results if code == 400)
        self.assertIn("non_field_errors", conflict_body)
        self.assertEqual(
            Category.objects.filter(company=self.company, name="Backend").count(),
            1,
        )

    def test_company_deleted_after_validation_returns_400_via_api(self):
        # POSTの検証後に企業が消えるDB競合をAPI経由で400へ変換できるか確認する。
        def delete_company_immediately_before_insert(sender, instance, **kwargs):
            # CategoryのINSERT直前に参照先Companyを削除して外部キー競合を起こす。
            if instance._state.adding and instance.name == "CompanyRace":
                Company.objects.filter(id=instance.company_id).delete()

        dispatch_uid = "category-api-company-delete-race"
        pre_save.connect(
            delete_company_immediately_before_insert,
            sender=Category,
            dispatch_uid=dispatch_uid,
            weak=False,
        )
        try:
            response = self.client.post(
                self.list_url,
                {"company": str(self.company.id), "name": "CompanyRace"},
                format="json",
            )
        finally:
            pre_save.disconnect(sender=Category, dispatch_uid=dispatch_uid)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("company", response.json())
        self.assertTrue(Company.objects.filter(id=self.company.id).exists())

    def test_parent_deleted_after_validation_returns_400_via_api(self):
        # POSTの検証後に親が消えるDB競合をAPI経由で400へ変換できるか確認する。
        parent = Category.objects.create(company=self.company, name="Engineering")

        def delete_parent_immediately_before_insert(sender, instance, **kwargs):
            # 子CategoryのINSERT直前に親Categoryを削除して外部キー競合を起こす。
            if instance._state.adding and instance.name == "ParentRace":
                Category.objects.filter(id=instance.parent_category_id).delete()

        dispatch_uid = "category-api-parent-delete-race"
        pre_save.connect(
            delete_parent_immediately_before_insert,
            sender=Category,
            dispatch_uid=dispatch_uid,
            weak=False,
        )
        try:
            response = self.client.post(
                self.list_url,
                {
                    "company": str(self.company.id),
                    "name": "ParentRace",
                    "parent_category": str(parent.id),
                },
                format="json",
            )
        finally:
            pre_save.disconnect(sender=Category, dispatch_uid=dispatch_uid)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.json())
        self.assertTrue(Category.objects.filter(id=parent.id).exists())

    def patch_parent(self, category_id, parent_id):
        # スレッド専用DB接続で親Categoryを変更するPATCHを送信する。
        connections.close_all()
        try:
            response = APIClient().patch(
                self.detail_url(category_id),
                {"parent_category": str(parent_id)},
                format="json",
            )
            return response.status_code, response.json()
        finally:
            connections.close_all()

    def patch_name(self, category_id):
        # スレッド専用DB接続でCategory名を変更するPATCHを送信する。
        connections.close_all()
        try:
            response = APIClient().patch(
                self.detail_url(category_id),
                {"name": "Updated"},
                format="json",
            )
            return response.status_code, response.json()
        finally:
            connections.close_all()

    def test_target_deleted_after_validation_returns_404_via_api(self):
        # PATCHの検証後・行ロック前に対象が削除された場合は404になることを確認する。
        category = Category.objects.create(company=self.company, name="Backend")
        control_connection = self.open_control_connection()
        released = False
        try:
            with control_connection.cursor() as cursor:
                cursor.execute(
                    'DELETE FROM "categories" WHERE "id" = %s',
                    (str(category.id),),
                )

            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self.patch_name, category.id)
                try:
                    self.wait_for_blocked_queries(
                        control_connection,
                        "FOR UPDATE",
                        expected_count=1,
                    )
                finally:
                    control_connection.commit()
                    released = True
                response_code, response_body = future.result(timeout=15)
        finally:
            if not released:
                control_connection.rollback()
            control_connection.close()

        self.assertEqual(response_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response_body)

    def test_concurrent_parent_updates_do_not_create_cycle(self):
        # 両PATCHを検証後のロック地点で同期し、片方だけ成功することを確認する。
        category_a = Category.objects.create(company=self.company, name="A")
        category_b = Category.objects.create(company=self.company, name="B")
        control_connection = self.open_control_connection()
        released = False
        try:
            with control_connection.cursor() as cursor:
                cursor.execute(
                    'SELECT "id" FROM "companies" WHERE "id" = %s '
                    "FOR NO KEY UPDATE",
                    (str(self.company.id),),
                )

            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = [
                    executor.submit(self.patch_parent, category_a.id, category_b.id),
                    executor.submit(self.patch_parent, category_b.id, category_a.id),
                ]
                try:
                    self.wait_for_blocked_queries(
                        control_connection,
                        "FOR NO KEY UPDATE",
                        expected_count=2,
                    )
                finally:
                    control_connection.commit()
                    released = True
                results = [future.result(timeout=15) for future in futures]
        finally:
            if not released:
                control_connection.rollback()
            control_connection.close()

        self.assertEqual(sorted(result[0] for result in results), [200, 400])
        conflict_body = next(body for code, body in results if code == 400)
        self.assertIn("parent_category", conflict_body)
        category_a.refresh_from_db()
        category_b.refresh_from_db()
        self.assertFalse(
            category_a.parent_category_id == category_b.id
            and category_b.parent_category_id == category_a.id
        )
