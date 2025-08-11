from api.models import Category
from api.models.category import MAX_DEPTH
from django.urls import reverse
from enum import IntEnum, auto
from freezegun import freeze_time
from parameterized import parameterized
from rest_framework import status
from rest_framework.test import APITestCase
from tests.factories import CategoryFactory, CompanyFactory
import pytest
import uuid


class CategoryType(IntEnum):
    BASIC = auto()
    WITH_PARENT = auto()
    MULTI_LEVEL = auto()
    WITH_CHILDREN = auto()


@pytest.mark.django_db
class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = CompanyFactory()
        self.list_url = reverse("category-list")
        self.detail_url = lambda pk: reverse("category-detail", kwargs={"pk": pk})

    def test_list(self):
        """カテゴリ一覧取得のテスト"""

        CategoryFactory.create_batch(3, company=self.company)
        CategoryFactory.create(company=CompanyFactory())  # 別会社のカテゴリ

        response = self.client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert len(response.data["results"]) == 4  # 全てのカテゴリが取得される

    @parameterized.expand(
        [
            # parent_category + 3 + 2 children
            (
                "company",
                lambda self: self.company.id,
                6,
            ),
            # すべてのカテゴリ名に'Category'が含まれる
            (
                "name",
                lambda self: "Category",
                7,
            ),
            # parent_category + 2 children
            (
                "parent_category",
                lambda self: self.parent_category.id,
                2,
            ),
        ]
    )
    def test_list_with_filters(self, filter_name, filter_value_func, expected_count):
        """フィルタリング付きカテゴリ一覧取得のテスト"""

        self.parent_category = CategoryFactory(company=self.company)
        CategoryFactory.create_batch(3, company=self.company)
        CategoryFactory.create_batch(2, company=self.company, parent_category=self.parent_category)
        CategoryFactory(company=CompanyFactory())  # 別会社のカテゴリ

        # フィルタ値の取得
        filter_value = filter_value_func(self)

        response = self.client.get(self.list_url, {filter_name: filter_value})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == expected_count

    @parameterized.expand(
        [
            ("name", "name"),
            ("-name", "-name"),
            ("created_at", "created_at"),
            ("-created_at", "-created_at"),
        ]
    )
    def test_list_ordering(self, ordering_param, expected_order):
        """並び替えのテスト"""

        # 2日前の日付から順番にカテゴリを作成
        with freeze_time("2025-01-01 12:00:00"):
            cat_c = CategoryFactory(company=self.company, name="C Category")  # 最も古い

        with freeze_time("2025-01-02 12:00:00"):
            cat_a = CategoryFactory(company=self.company, name="A Category")  # 中間の日付

        with freeze_time("2025-01-03 12:00:00"):
            cat_b = CategoryFactory(company=self.company, name="B Category")  # 最も新しい

        response = self.client.get(self.list_url, {"ordering": ordering_param})

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data

        # レスポンスから作成したカテゴリだけを抽出
        created_category_ids = {str(cat_a.id), str(cat_b.id), str(cat_c.id)}
        result_items = [
            item for item in response.data["results"] if item["id"] in created_category_ids
        ]

        # 実際に返された順序
        actual_ids = [item["id"] for item in result_items]

        # 期待される順序
        if expected_order == "name":
            expected_ids = [str(cat_a.id), str(cat_b.id), str(cat_c.id)]
        elif expected_order == "-name":
            expected_ids = [str(cat_c.id), str(cat_b.id), str(cat_a.id)]
        elif expected_order == "created_at":
            expected_ids = [str(cat_c.id), str(cat_a.id), str(cat_b.id)]  # 古い順
        elif expected_order == "-created_at":
            expected_ids = [str(cat_b.id), str(cat_a.id), str(cat_c.id)]  # 新しい順

        # 順序が正しいことを確認
        assert actual_ids == expected_ids, (
            f"For ordering {ordering_param}: expected {expected_ids}, got {actual_ids}"
        )

    def test_list_pagination(self):
        """ページネーションのテスト"""

        CategoryFactory.create_batch(25, company=self.company)

        response = self.client.get(self.list_url, {"page": 2, "page_size": 10})

        assert response.status_code == status.HTTP_200_OK
        assert "count" in response.data
        assert response.data["count"] == 25
        assert len(response.data["results"]) == 10
        assert response.data["next"] is True
        assert response.data["previous"] is True

    @parameterized.expand(
        [
            (CategoryType.BASIC),
            (CategoryType.WITH_PARENT),
            (CategoryType.MULTI_LEVEL),
            (CategoryType.WITH_CHILDREN),
        ]
    )
    def test_retrieve(self, category_type):
        """カテゴリ詳細取得のテスト - 様々なケース"""

        # テストケースごとの前提条件を作成
        with freeze_time("2025-01-01 12:00:00"):
            # カテゴリタイプによって異なる階層構造を作成
            match category_type:
                case CategoryType.BASIC:
                    category = CategoryFactory(company=self.company, name="テストカテゴリ")
                case CategoryType.WITH_PARENT:
                    parent = CategoryFactory(company=self.company, name="親カテゴリ")
                    category = CategoryFactory(
                        company=self.company, name="子カテゴリ", parent_category=parent
                    )
                case CategoryType.MULTI_LEVEL:
                    grandparent = CategoryFactory(company=self.company, name="祖父カテゴリ")
                    parent = CategoryFactory(
                        company=self.company,
                        name="親カテゴリ",
                        parent_category=grandparent,
                    )
                    category = CategoryFactory(
                        company=self.company, name="孫カテゴリ", parent_category=parent
                    )
                case CategoryType.WITH_CHILDREN:
                    category = CategoryFactory(company=self.company, name="親カテゴリ")
                    CategoryFactory(
                        company=self.company,
                        name="子カテゴリ1",
                        parent_category=category,
                    )
                    CategoryFactory(
                        company=self.company,
                        name="子カテゴリ2",
                        parent_category=category,
                    )

        response = self.client.get(self.detail_url(category.id))

        # 共通アサーション
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(category.id)
        assert response.data["name"] == category.name
        assert response.data["company"] == self.company.id
        assert "created_at" in response.data
        assert "updated_at" in response.data

        # カテゴリタイプごとの追加検証
        match category_type:
            case CategoryType.BASIC:
                assert response.data["parent_category"] is None
                assert response.data["depth"] == 0
                assert len(response.data["ancestors"]) == 0
                assert len(response.data["children"]) == 0

            case CategoryType.WITH_PARENT:
                assert response.data["parent_category"] == category.parent_category.id
                assert response.data["depth"] == 1
                assert len(response.data["ancestors"]) == 1
                assert response.data["ancestors"][0]["id"] == str(category.parent_category.id)
                assert response.data["ancestors"][0]["name"] == category.parent_category.name
                assert len(response.data["children"]) == 0

            case CategoryType.MULTI_LEVEL:
                assert response.data["parent_category"] == category.parent_category.id
                assert response.data["depth"] == 2
                assert len(response.data["ancestors"]) == 2
                parent_id = str(category.parent_category.id)
                grandparent_id = str(category.parent_category.parent_category.id)
                ancestor_ids = [a["id"] for a in response.data["ancestors"]]
                assert parent_id in ancestor_ids
                assert grandparent_id in ancestor_ids
                assert len(response.data["children"]) == 0

            case CategoryType.WITH_CHILDREN:
                assert response.data["parent_category"] is None
                assert response.data["depth"] == 0
                assert len(response.data["ancestors"]) == 0
                assert len(response.data["children"]) == 2
                # 子カテゴリの名前を確認
                child_names = [c["name"] for c in response.data["children"]]
                assert "子カテゴリ1" in child_names
                assert "子カテゴリ2" in child_names

    def test_retrieve_not_found(self):
        """存在しないカテゴリの詳細取得テスト"""

        response = self.client.get(self.detail_url(uuid.uuid4()))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create(self):
        """カテゴリ作成のテスト"""

        data = {"name": "New Category", "company": str(self.company.id)}

        response = self.client.post(self.list_url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert not hasattr(response, "data") or response.data is None or response.data == ""
        assert Category.objects.filter(name=data["name"]).exists()

    @parameterized.expand(
        [
            (
                "",
                "This field may not be blank.",
            ),  # 空文字列の場合のDRFデフォルトメッセージ
            (
                "a",
                "カテゴリ名は2文字以上で入力してください",
            ),
            (
                "カテゴリ@#$",
                "カテゴリ名には英数字、日本語、ハイフン、アンダースコアのみ使用できます",
            ),
        ]
    )
    def test_create_invalid_name(self, invalid_name, expected_error):
        """無効なカテゴリ名での作成テスト"""

        data = {"name": invalid_name, "company": str(self.company.id)}

        response = self.client.post(self.list_url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert expected_error in str(response.data["name"])

    def test_create_with_parent_category(self):
        """親カテゴリ付きでの作成テスト"""

        parent = CategoryFactory(company=self.company)

        data = {
            "name": "Child Category",
            "company": str(self.company.id),
            "parent_category": str(parent.id),
        }

        response = self.client.post(self.list_url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert not hasattr(response, "data") or response.data is None or response.data == ""
        # データベースで親カテゴリが設定されていることを確認
        created_category = Category.objects.get(name=data["name"])
        assert created_category.parent_category.id == parent.id

    def test_create_with_different_company_parent(self):
        """異なる会社の親カテゴリでの作成テスト"""

        other_company = CompanyFactory()
        parent = CategoryFactory(company=other_company)

        data = {
            "name": "Child Category",
            "company": str(self.company.id),
            "parent_category": str(parent.id),
        }

        response = self.client.post(self.list_url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "parent_category" in response.data

    def test_create_exceeding_max_depth(self):
        """最大階層を超える作成テスト"""

        parent = CategoryFactory(company=self.company)
        for i in range(MAX_DEPTH):
            parent = CategoryFactory(company=self.company, parent_category=parent)

        data = {
            "name": "Too Deep Category",
            "company": str(self.company.id),
            "parent_category": str(parent.id),
        }

        response = self.client.post(self.list_url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "parent_category" in response.data

    def test_update(self):
        """カテゴリ更新のテスト"""

        category = CategoryFactory(company=self.company)

        data = {"name": "Updated Category", "company": str(self.company.id)}

        response = self.client.put(self.detail_url(category.id), data, format="json")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not hasattr(response, "data") or response.data is None or response.data == ""

        category.refresh_from_db()
        assert category.name == data["name"]

    def test_update_self_as_parent(self):
        """自分自身を親に設定する更新テスト"""

        category = CategoryFactory(company=self.company)

        data = {
            "name": category.name,
            "company": str(self.company.id),
            "parent_category": str(category.id),  # 自分自身を親に
        }

        response = self.client.put(self.detail_url(category.id), data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "parent_category" in response.data

    def test_update_descendant_as_parent(self):
        """子孫を親に設定する更新テスト"""

        parent = CategoryFactory(company=self.company)
        child = CategoryFactory(company=self.company, parent_category=parent)

        data = {
            "name": parent.name,
            "company": str(self.company.id),
            "parent_category": str(child.id),  # 子を親に
        }

        response = self.client.put(self.detail_url(parent.id), data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "parent_category" in response.data

    def test_destroy(self):
        """カテゴリ削除のテスト"""

        category = CategoryFactory(company=self.company)
        category_id = category.id

        response = self.client.delete(self.detail_url(category_id))

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Category.objects.filter(id=category_id).exists()

    def test_destroy_with_children(self):
        """子カテゴリがある場合の削除テスト"""

        parent = CategoryFactory(company=self.company)
        category_id = parent.id
        CategoryFactory(company=self.company, parent_category=parent)

        response = self.client.delete(self.detail_url(category_id))

        assert response.status_code == status.HTTP_204_NO_CONTENT
        # 子カテゴリがある場合は削除されない
        assert Category.objects.filter(id=category_id).exists()

    def test_destroy_not_found(self):
        """存在しないカテゴリの削除テスト"""

        response = self.client.delete(self.detail_url(uuid.uuid4()))

        assert response.status_code == status.HTTP_204_NO_CONTENT
