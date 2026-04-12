import uuid
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models.company import Company
from api.models.category import Category

class CategoryViewTests(APITestCase):

    def setUp(self):
        # テスト用データの作成
        self.company = Company.objects.create(name="テスト企業")
        self.other_company = Company.objects.create(name="他社")

        # カテゴリの作成（ルート）
        self.cat_food = Category.objects.create(
            name="食品", company=self.company
        )
        self.cat_elec = Category.objects.create(
            name="電化製品", company=self.company
        )

        # 子カテゴリの作成
        self.cat_vege = Category.objects.create(
            name="野菜", company=self.company, parent_category=self.cat_food
        )

    def _create_category(self, name, parent=None, company=None):
        return Category.objects.create(
            name=name,
            company=company or self.company,
            parent_category=parent
        )

    # ── List / Retrieve ───────────────────────────────

    def test_list(self):
        """
        正常系: parent_category_id パラメータなし、または空文字指定の場合、ルートカテゴリのみがページネーション形式で取得される
        """
        cases = [
            ("指定なし", {}),
            ("空文字", {"parent_category_id": ""}),
        ]

        for desc, params in cases:
            with self.subTest(case=desc):
                response = self.client.get(reverse("category-list"), params)

                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertIn("results", response.data)
                results = response.data["results"]
                # すべて親が None（ルート）であること
                self.assertTrue(all(item["parent_category"] is None for item in results))
                self.assertEqual(len(results), 2, f"{desc}の件数が一致しません")
                names = [item["name"] for item in results]
                self.assertIn("食品", names)
                self.assertIn("電化製品", names)
                self.assertNotIn("野菜", names)

    def test_list_multi_tenant_isolation(self):
        """
        正常系: 他社のカテゴリがリストに含まれないことを検証
        """
        # 他社カテゴリを作成
        other_cat = Category.objects.create(
            name="他社カテゴリ",
            company=self.other_company
        )

        response = self.client.get(reverse("category-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]

        # 自分の企業のカテゴリのみが含まれていることを確認
        names = [item["name"] for item in results]
        self.assertNotIn("他社カテゴリ", names)
        # 自分の企業のルートカテゴリ（食品・電化製品）のみであることを保証
        self.assertEqual(len(results), 2)

    def test_list_children_by_parent_id(self):
        """
        正常系: parent_category_id 指定時、その直下の子のみ取得される
        """
        response = self.client.get(
            reverse("category-list"),
            {"parent_category_id": self.cat_food.id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(len(results), 1)

        # 取得データの詳細検証
        target_category = results[0]
        self.assertEqual(target_category["name"], "野菜")

        # 親カテゴリ情報の検証 (IDと名前が含まれているか)
        parent_info = target_category["parent_category"]
        self.assertIsNotNone(parent_info, "親カテゴリ情報が含まれていません")
        self.assertEqual(parent_info["id"], str(self.cat_food.id))
        self.assertEqual(parent_info["name"], "食品")

        # 直下の子カテゴリであることの検証
        # 取得されたカテゴリの parent_category が、指定した parent_category_id と一致することを確認
        self.assertTrue(
            all(item["parent_category"]["id"] == str(self.cat_food.id) for item in results),
            "指定した親カテゴリ以外のカテゴリが含まれています"
        )

    def test_list_non_existent_uuid_returns_empty_list(self):
        """正常系: 存在しないUUIDを親IDに指定した場合、200 OK と空のリストが返る"""

        # カテゴリレコードに存在しないUUIDを生成
        non_existent_id = uuid.uuid4()
        self.assertFalse(
            Category.objects.filter(id=non_existent_id).exists(),
            f"UUID: {non_existent_id} はすでに登録されています。"
        )

        response = self.client.get(
            reverse("category-list"),
            {"parent_category_id": str(non_existent_id)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(len(results), 0, "存在しない親IDに対してデータが返されています")
        self.assertEqual(response.data["count"], 0)

    def test_children_count_annotation(self):
        """
        正常系: 子カテゴリの数が正しく計算されているか
        """
        response = self.client.get(reverse("category-list"))

        results = response.data["results"]
        food_data = next(item for item in results if item["name"] == "食品")
        self.assertEqual(food_data["children_count"], 1) # 野菜がある

    def test_list_invalid_parent_id_returns_400(self):
        """
        異常系: 無効な形式の parent_category_id 指定時、400エラーが返ることを検証
        """

        # 検証する無効なパターンのリスト
        invalid_patterns = [
            ("文字列のnull", "null"),
            ("ハッシュ", "abc12345"),
            ("UUIDフォーマット不正", "9230ef05-e0f6-4283"),
            ("特殊文字", "@#$%^&*"),
        ]

        for desc, invalid_id in invalid_patterns:
            with self.subTest(case=desc):
                response = self.client.get(
                    reverse("category-list"),
                    {"parent_category_id": invalid_id}
                )

                # 400エラーが返ることを確認
                self.assertEqual(
                    response.status_code,
                    status.HTTP_400_BAD_REQUEST,
                    f"{desc} の時に400エラーが返却されませんでした。"
                )

                # エラーメッセージに該当のフィールド名が含まれているか確認
                self.assertIn("parent_category_id", response.data)
                self.assertEqual(
                    response.data["parent_category_id"][0],
                    "有効なカテゴリIDを指定してください。"
                )

    def test_retrieve(self):
        """
        正常系: カテゴリ詳細が取得され、親情報と子リストが正しく含まれる
        """
        # ルートカテゴリ「食品」を取得（子に「野菜」を持つ）
        response = self.client.get(reverse("category-detail", args=[self.cat_food.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 基本情報の検証
        self.assertEqual(response.data["name"], "食品")
        self.assertEqual(response.data["children_count"], 1)

        # 親情報の検証（ルートなので None であること）
        self.assertIsNone(response.data["parent_category"])

        # 子カテゴリリストの検証
        self.assertIn("children", response.data)
        children = response.data["children"]
        self.assertEqual(len(children), 1)
        self.assertEqual(children[0]["id"], str(self.cat_vege.id))
        self.assertEqual(children[0]["name"], "野菜")

    def test_retrieve_child_category_details(self):
        """
        正常系: 子カテゴリ取得時、親の情報（IDと名前）が取得できる
        """
        # 子カテゴリ「野菜」を取得
        response = self.client.get(reverse("category-detail", args=[self.cat_vege.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 親情報の検証（CategorySimpleSerializer の形式）
        parent = response.data["parent_category"]
        self.assertIsNotNone(parent)
        self.assertEqual(parent["id"], str(self.cat_food.id))
        self.assertEqual(parent["name"], "食品")

    def test_retrieve_children_sorted_by_name(self):
        """
        正常系: 詳細取得時の children は name の昇順で返る
        """
        parent = self._create_category("並び順親")
        child_b = self._create_category("banana", parent=parent)
        child_a = self._create_category("apple", parent=parent)

        response = self.client.get(reverse("category-detail", args=[parent.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        children = response.data["children"]
        self.assertEqual(len(children), 2)
        self.assertEqual([child["name"] for child in children], ["apple", "banana"])
        self.assertEqual([child["id"] for child in children], [str(child_a.id), str(child_b.id)])

    def test_retrieve_not_found(self):
        """
        異常系: 存在しない ID、または形式が不正な ID の場合は 404 を返す
        """
        # 存在しないUUID
        non_existent_id = uuid.uuid4()
        self.assertFalse(
            Category.objects.filter(id=non_existent_id).exists(),
            f"UUID: {non_existent_id} はすでに登録されています。"
        )

        response = self.client.get(reverse("category-detail", args=[non_existent_id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # 不正な形式
        # Django の DefaultRouter は UUID 形式に一致しない URL を解決できないため 404 を返す
        response = self.client.get(reverse("category-detail", args=["invalid-uuid"]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_multi_tenant_isolation(self):
        """
        異常系: 他社のカテゴリIDを直接指定した場合、404 Not Found を返す
        """
        # 他社のカテゴリを作成
        other_cat = Category.objects.create(
            name="他社データ",
            company=self.other_company
        )

        # IDを直接指定してアクセス
        response = self.client.get(reverse("category-detail", args=[other_cat.id]))

        # 存在していても、自社のスコープ外なので 404 を返却
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ── Create / Update ───────────────────────────────

    def test_create(self):
        """
        正常系: 親カテゴリを指定しない場合にルートカテゴリ作成が成功し、企業が紐付けされる
        """
        data = {"name": "日用品"}
        # 親を指定しないリクエスト
        response = self.client.post(reverse("category-list"), data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_cat = Category.objects.get(name="日用品")
        self.assertIsNone(new_cat.parent_category)
        self.assertEqual(new_cat.company, self.company)

    def test_create_root_variations(self):
        """
        正常系: parent_category が空文字、null の場合、ルートカテゴリとして作成される
        """
        cases = [
            ("空文字", {"name": "文房具", "parent_category": ""}),
            ("明示的なnull", {"name": "キッチン用品", "parent_category": None}),
        ]

        for desc, data in cases:
            with self.subTest(case=desc):
                # 常に format="json" を使うことで None (null) も安全に送信可能
                response = self.client.post(reverse("category-list"), data, format="json")

                self.assertEqual(
                    response.status_code,
                    status.HTTP_201_CREATED,
                    f"{desc} の作成に失敗しました"
                )

                # 作成されたカテゴリの親が None であることを確認
                new_cat = Category.objects.get(name=data["name"])
                self.assertIsNone(
                    new_cat.parent_category,
                    f"{desc} の親が None になっていません"
                )
                self.assertEqual(new_cat.company, self.company)

    def test_create_grandchild_category(self):
        """
        正常系: 子カテゴリを親として、孫カテゴリを作成できる
        """
        # 「野菜 (self.cat_vege)」を親にして「葉物野菜」を作成
        data = {
            "name": "葉物野菜",
            "parent_category": str(self.cat_vege.id)
        }
        response = self.client.post(reverse("category-list"), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_cat = Category.objects.get(name="葉物野菜")
        self.assertEqual(new_cat.parent_category, self.cat_vege)
        # 3階層目でも企業が正しく引き継がれているか
        self.assertEqual(new_cat.company, self.company)

    def test_create_prevent_other_company_parent(self):
        """
        異常系: 他社のカテゴリを親に指定すると 400 エラー
        """
        other_cat = self._create_category("他社カテゴリ", company=self.other_company)
        data = {"name": "不正な子カテゴリ", "parent_category": other_cat.id}
        response = self.client.post(reverse("category-list"), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)
        self.assertEqual(response.data["parent_category"][0], "指定された親カテゴリは同一企業に属していません。")

    def test_create_duplicate_name_in_same_company(self):
        """
        異常系: 同一企業内で既に存在する名前のカテゴリを作成しようとすると 400エラー
        """
        # setUp で作成済みの「食品」と同じ名前でリクエスト
        data = {"name": "食品"}
        response = self.client.post(reverse("category-list"), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertEqual(
            response.data["non_field_errors"][0],
            "既に同名のカテゴリが存在します。"
        )

    def test_create_invalid_inputs(self):
        """
        異常系: 不正な入力値に対して 400エラーを返す
        """
        cases = [
            ("名前が空", {"name": ""}, "name"),
            ("存在しない親ID", {"name": "子", "parent_category": str(uuid.uuid4())}, "parent_category"),
            ("親IDが不正形式", {"name": "子", "parent_category": "invalid-uuid-format"}, "parent_category"),
        ]

        for desc, data, error_field in cases:
            with self.subTest(case=desc):
                response = self.client.post(reverse("category-list"), data, format="json")

                # 400エラーが返ることを確認
                self.assertEqual(
                    response.status_code,
                    status.HTTP_400_BAD_REQUEST,
                    f"{desc} の時に400エラーが返却されませんでした。"
                )

                # 期待したフィールドにエラーが含まれていることを確認
                self.assertIn(
                    error_field,
                    response.data,
                    f"{desc} の時にエラーフィールド '{error_field}' が含まれていません。"
                )

    def test_update(self):
        """
        正常系: カテゴリ名の変更が成功する
        """
        url = reverse("category-detail", args=[self.cat_food.id])
        data = {"name": "新・食品カテゴリ"}

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cat_food.refresh_from_db()
        self.assertEqual(self.cat_food.name, "新・食品カテゴリ")
        # 企業が変わっていないこと
        self.assertEqual(self.cat_food.company, self.company)

    def test_update_same_name_self_success(self):
        """
        正常系: 自分の現在の名前と同じ名前で更新（保存）してもエラーにならない
        """
        url = reverse("category-detail", args=[self.cat_food.id])
        data = {"name": self.cat_food.name}

        response = self.client.patch(url, data, format="json")

        # 自分の名前との重複は validator が賢くスルーしてくれるはず
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_name_too_long_fails(self):
        """
        異常系: 256文字以上の名前で更新しようとすると 400エラー
        """
        url = reverse("category-detail", args=[self.cat_food.id])
        data = {"name": "a" * 256}

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_update_parent_field_not_allowed(self):
        """
        異常系: 更新時に parent_category フィールドが含まれていると 400エラー
        """
        url = reverse("category-detail", args=[self.cat_vege.id])

        cases = [
            ("現在と同じ親ID", str(self.cat_food.id), "親カテゴリの変更は未サポート"),
            ("ルート化(None)", None, "親カテゴリの変更は未サポート"),
            ("空文字", "", "親カテゴリの変更は未サポート"),
            ("不正な形式", "invalid-uuid", "is not a valid UUID"),
        ]

        for desc, p_id, expected_msg in cases:
            with self.subTest(case=desc):
                response = self.client.patch(url, {"parent_category": p_id}, format="json")

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(expected_msg, str(response.data["parent_category"][0]))

    def test_update_duplicate_name_fails(self):
        """
        異常系: 他の既存カテゴリと同じ名前に変更しようとすると 400エラー
        """
        # 「食品」を「野菜」という名前に変更しようとする（野菜は既に存在）
        url = reverse("category-detail", args=[self.cat_food.id])
        data = {"name": self.cat_vege.name}

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertEqual(
            response.data["non_field_errors"][0],
            "既に同名のカテゴリが存在します。"
        )

    def test_update_other_company_category_fails(self):
        """
        異常系: 他社のカテゴリを更新しようとすると 404 エラー
        """
        other_cat = self._create_category("他社データ", company=self.other_company)
        url = reverse("category-detail", args=[other_cat.id])
        data = {"name": "他社カテゴリ更新"}

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_is_not_allowed(self):
        """
        異常系: PUTリクエストは許可されていないため 405 エラーになる
        """
        url = reverse("category-detail", args=[self.cat_food.id])
        data = {"name": "PUTは禁止"}

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # ── Destroy ───────────────────────────────────────

    def test_destroy(self):
        """
        正常系: 子カテゴリを持たないカテゴリは削除できる
        """
        cat = self._create_category("削除用")
        url = reverse("category-detail", args=[cat.id])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=cat.id).exists())

    def test_destroy_prevent_if_has_children(self):
        """
        異常系: 子カテゴリを持つカテゴリを削除しようとすると 400エラー
        """
        # self.cat_food は setUp で self.cat_vege を子に持っている想定
        url = reverse("category-detail", args=[self.cat_food.id])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("子カテゴリが存在するため削除できません", str(response.data["detail"]))
        # レコードが削除されていないことを確認
        self.assertTrue(Category.objects.filter(id=self.cat_food.id).exists())

    def test_destroy_other_company_category_fails(self):
        """
        異常系: 他社のカテゴリを削除しようとすると 404エラー
        """
        other_cat = self._create_category("他社データ", company=self.other_company)
        url = reverse("category-detail", args=[other_cat.id])

        response = self.client.delete(url)

        # 権限がないデータは「存在しない」ものとして 404 を返却
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # レコードが削除されていないことを確認
        self.assertTrue(Category.objects.filter(id=other_cat.id).exists())
