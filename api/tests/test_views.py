import uuid
from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Category, Company


class CategoryViewTests(APITestCase):
    """カテゴリ API(/api/categories/)のテスト。

    共通データとして、企業 2 件(company, other_company)と、company に属する親子のカテゴリ(parent, child)を用意する。
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.company = Company.objects.create(name="company")
        cls.other_company = Company.objects.create(name="other company")
        cls.parent = Category.objects.create(company=cls.company, name="parent")
        cls.child = Category.objects.create(company=cls.company, name="child", parent_category=cls.parent)

    def list_url(self) -> str:
        return reverse("category-list")

    def detail_url(self, pk: uuid.UUID | str) -> str:
        return reverse("category-detail", args=[pk])

    # list

    def test_list(self):
        """全件が返り、各要素が API の全フィールドを持つこと。"""
        response = self.client.get(self.list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual([item["id"] for item in response.data], [str(self.parent.id), str(self.child.id)])
        self.assertEqual(
            set(response.data[0].keys()), {"id", "company", "name", "parent_category", "created_at", "updated_at"}
        )

    def test_list_ordered_by_created_at(self):
        """作成日時の昇順で返り、同時刻なら id の昇順になること。

        挿入順・id 順・作成日時順がそれぞれ異なるデータにして、並び順を指定しないと結果が変わるようにする。
        created_at は auto_now_add のため、作成後に update で書き換える。
        """
        Category.objects.all().delete()
        base = timezone.now()
        later = Category.objects.create(id=uuid.UUID(int=2), company=self.company, name="later")
        same_time_large_id = Category.objects.create(id=uuid.UUID(int=3), company=self.company, name="large id")
        same_time_small_id = Category.objects.create(id=uuid.UUID(int=1), company=self.company, name="small id")
        Category.objects.filter(id=later.id).update(created_at=base + timedelta(seconds=1))
        Category.objects.filter(id__in=[same_time_large_id.id, same_time_small_id.id]).update(created_at=base)

        response = self.client.get(self.list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [item["id"] for item in response.data],
            [str(same_time_small_id.id), str(same_time_large_id.id), str(later.id)],
        )

    def test_list_empty(self):
        """カテゴリが無いときは 404 ではなく空配列が返ること。"""
        Category.objects.all().delete()

        response = self.client.get(self.list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    # retrieve

    def test_retrieve(self):
        """指定したカテゴリが返り、company と parent_category が ID で表現されること。"""
        response = self.client.get(self.detail_url(self.child.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.child.id))
        self.assertEqual(response.data["company"], self.company.id)
        self.assertEqual(response.data["name"], "child")
        self.assertEqual(response.data["parent_category"], self.parent.id)

    def test_retrieve_root_category_has_null_parent(self):
        """親を持たないカテゴリは parent_category が null で返ること。"""
        response = self.client.get(self.detail_url(self.parent.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data["parent_category"])

    def test_retrieve_not_found(self):
        """存在しない ID を指定すると 404 になること。"""
        response = self.client.get(self.detail_url(uuid.uuid4()))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_invalid_uuid(self):
        """UUID として不正な ID を指定しても 500 にならず 404 になること。"""
        response = self.client.get(self.detail_url("invalid"))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # create

    def test_create(self):
        """company と name だけで作成でき、parent_category は null になること。"""
        response = self.client.post(self.list_url(), {"company": self.company.id, "name": "new"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        category = Category.objects.get(id=response.data["id"])
        self.assertEqual(category.company, self.company)
        self.assertEqual(category.name, "new")
        self.assertIsNone(category.parent_category)

    def test_create_with_parent(self):
        """同じ企業のカテゴリを親に指定して作成できること。"""
        data = {"company": self.company.id, "name": "new", "parent_category": self.parent.id}

        response = self.client.post(self.list_url(), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.get(id=response.data["id"]).parent_category, self.parent)

    def test_create_trims_name(self):
        """name の前後の空白が除かれて保存されること。"""
        response = self.client.post(self.list_url(), {"company": self.company.id, "name": "  new  "}, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.get(id=response.data["id"]).name, "new")

    def test_create_name_max_length(self):
        """name はモデルの上限である 255 文字まで受け付けること(境界値)。"""
        response = self.client.post(self.list_url(), {"company": self.company.id, "name": "a" * 255}, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_name(self):
        """空文字・空白のみ・null・256 文字の name は 400 になり、作成されないこと。"""
        for name in ["", "   ", None, "a" * 256]:
            with self.subTest(name=name):
                response = self.client.post(self.list_url(), {"company": self.company.id, "name": name}, format="json")

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn("name", response.data)
        self.assertEqual(Category.objects.count(), 2)

    def test_create_missing_required_fields(self):
        """必須の company と name が欠けていると、そのフィールドのエラーで 400 になること。"""
        for field, data in [("company", {"name": "new"}), ("name", {"company": self.company.id})]:
            with self.subTest(field=field):
                response = self.client.post(self.list_url(), data, format="json")

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(field, response.data)

    def test_create_invalid_company(self):
        """存在しない、または UUID として不正な company は 500 にならず 400 になること。"""
        for company in [uuid.uuid4(), "invalid"]:
            with self.subTest(company=company):
                response = self.client.post(self.list_url(), {"company": company, "name": "new"}, format="json")

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn("company", response.data)

    def test_create_invalid_parent_category(self):
        """存在しない、または UUID として不正な parent_category は 500 にならず 400 になること。"""
        for parent in [uuid.uuid4(), "invalid"]:
            with self.subTest(parent=parent):
                data = {"company": self.company.id, "name": "new", "parent_category": parent}

                response = self.client.post(self.list_url(), data, format="json")

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn("parent_category", response.data)

    def test_create_duplicate_name_in_same_company(self):
        """同じ企業内の重複した name は、DB の制約違反(500)になる前に 400 で弾かれること。

        前後の空白を除いた後の値で重複を判定することも確かめる。
        """
        for name in ["parent", "  parent  "]:
            with self.subTest(name=name):
                response = self.client.post(self.list_url(), {"company": self.company.id, "name": name}, format="json")

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(response.data["non_field_errors"][0].code, "unique")
        self.assertEqual(Category.objects.count(), 2)

    def test_create_same_name_in_other_company(self):
        """name の一意性は企業ごとなので、別の企業なら同じ name で作成できること。"""
        response = self.client.post(self.list_url(), {"company": self.other_company.id, "name": "parent"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_parent_in_other_company(self):
        """別の企業のカテゴリを親に指定すると 400 になり、作成されないこと。"""
        data = {"company": self.other_company.id, "name": "new", "parent_category": self.parent.id}

        response = self.client.post(self.list_url(), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)
        self.assertFalse(Category.objects.filter(name="new").exists())

    def test_create_ignores_read_only_fields(self):
        """id と created_at はクライアントから指定しても無視され、サーバー側で採番されること。"""
        given_id = uuid.uuid4()
        data = {"id": given_id, "company": self.company.id, "name": "new", "created_at": "2000-01-01T00:00:00Z"}

        response = self.client.post(self.list_url(), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(response.data["id"], str(given_id))
        self.assertNotEqual(response.data["created_at"][:4], "2000")

    # update

    def test_update(self):
        """PUT で name と parent_category を更新でき、parent_category は null で解除できること。"""
        data = {"company": self.company.id, "name": "renamed", "parent_category": None}

        response = self.client.put(self.detail_url(self.child.id), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.child.refresh_from_db()
        self.assertEqual(self.child.name, "renamed")
        self.assertIsNone(self.child.parent_category)

    def test_update_without_parent_keeps_parent(self):
        """PUT で任意項目の parent_category を省略すると、null にはならず現在の親が維持されること。

        DRF では必須でないフィールドを省略すると更新対象にならないため。親を解除するには null を明示して送る。
        """
        response = self.client.put(
            self.detail_url(self.child.id), {"company": self.company.id, "name": "renamed"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.child.refresh_from_db()
        self.assertEqual(self.child.name, "renamed")
        self.assertEqual(self.child.parent_category, self.parent)

    def test_update_missing_required_fields(self):
        """PUT は全体の置き換えなので、必須の name が欠けていると 400 になること。"""
        response = self.client.put(self.detail_url(self.child.id), {"company": self.company.id}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_partial_update(self):
        """PATCH では送ったフィールドだけが更新され、他のフィールドは変わらないこと。"""
        response = self.client.patch(self.detail_url(self.child.id), {"name": "renamed"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.child.refresh_from_db()
        self.assertEqual(self.child.name, "renamed")
        self.assertEqual(self.child.company, self.company)
        self.assertEqual(self.child.parent_category, self.parent)

    def test_partial_update_set_and_clear_parent(self):
        """PATCH で親を設定でき、null を送ると解除できること。"""
        category = Category.objects.create(company=self.company, name="new")

        response = self.client.patch(self.detail_url(category.id), {"parent_category": self.child.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        category.refresh_from_db()
        self.assertEqual(category.parent_category, self.child)

        response = self.client.patch(self.detail_url(category.id), {"parent_category": None}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        category.refresh_from_db()
        self.assertIsNone(category.parent_category)

    def test_update_keeps_own_name(self):
        """自分自身の現在の name は、重複とみなされず更新できること。"""
        data = {"company": self.company.id, "name": "child", "parent_category": self.parent.id}

        response = self.client.put(self.detail_url(self.child.id), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_duplicate_name_in_same_company(self):
        """company を省略した PATCH でも、同じ企業内の他のカテゴリと同じ name は 400 になること。"""
        response = self.client.patch(self.detail_url(self.child.id), {"name": "parent"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["non_field_errors"][0].code, "unique")
        self.child.refresh_from_db()
        self.assertEqual(self.child.name, "child")

    def test_update_company_cannot_be_changed(self):
        """作成後に company を別の企業へ変更しようとすると 400 になり、変更されないこと。"""
        response = self.client.patch(self.detail_url(self.parent.id), {"company": self.other_company.id}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("company", response.data)
        self.parent.refresh_from_db()
        self.assertEqual(self.parent.company, self.company)

    def test_update_parent_in_other_company(self):
        """別の企業のカテゴリを親に指定すると 400 になること。"""
        other = Category.objects.create(company=self.other_company, name="other")

        response = self.client.patch(self.detail_url(self.child.id), {"parent_category": other.id}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)

    def test_update_parent_circular_reference(self):
        """自分自身・子・孫を親に指定すると、循環になるため 400 になり、変更されないこと。

        孫のケースで、直接の子だけでなく祖先方向にたどって判定していることを確かめる。
        """
        grandchild = Category.objects.create(company=self.company, name="grandchild", parent_category=self.child)
        for new_parent in [self.parent, self.child, grandchild]:
            with self.subTest(new_parent=new_parent.name):
                response = self.client.patch(
                    self.detail_url(self.parent.id), {"parent_category": new_parent.id}, format="json"
                )

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn("parent_category", response.data)
        self.parent.refresh_from_db()
        self.assertIsNone(self.parent.parent_category)

    def test_update_not_found(self):
        """存在しない ID を更新しようとすると 404 になること。"""
        response = self.client.patch(self.detail_url(uuid.uuid4()), {"name": "renamed"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # destroy

    def test_destroy(self):
        """指定したカテゴリが削除され、204 が返ること。"""
        response = self.client.delete(self.detail_url(self.child.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.child.id).exists())

    def test_destroy_sets_children_parent_to_null(self):
        """親を削除しても子は残り、モデルの on_delete=SET_NULL に従って parent_category が null になること。"""
        response = self.client.delete(self.detail_url(self.parent.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.child.refresh_from_db()
        self.assertIsNone(self.child.parent_category)

    def test_destroy_not_found(self):
        """存在しない ID を削除しようとすると 404 になること。"""
        response = self.client.delete(self.detail_url(uuid.uuid4()))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
