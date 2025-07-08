from uuid import UUID

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company


class CategoryViewSetTests(APITestCase):
    def setUp(self) -> None:
        self.company = Company.objects.create(name="Alpha")
        self.other_company = Company.objects.create(name="Beta")
        self.parent = Category.objects.create(
            company=self.company,
            name="Parent",
        )
        self.child = Category.objects.create(
            company=self.company,
            name="Child",
            parent_category=self.parent,
        )
        self.list_url = reverse("category-list")

    def detail_url(self, category: Category) -> str:
        return reverse("category-detail", args=[str(category.pk)])

    # 一覧取得
    def test_list_all(self) -> None:
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_filter_by_company(self) -> None:
        response = self.client.get(self.list_url, {"company": str(self.company.pk)})
        self.assertEqual(len(response.data), 2)
        response = self.client.get(
            self.list_url, {"company": str(self.other_company.pk)}
        )
        self.assertEqual(len(response.data), 0)

    # 詳細取得
    def test_retrieve_detail(self) -> None:
        response = self.client.get(self.detail_url(self.child))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(UUID(response.data["id"]), self.child.pk)

    # 作成
    def test_create_success(self) -> None:
        payload = {
            "company": str(self.company.pk),
            "name": "Snacks",
            "parent_category": str(self.parent.pk),
        }
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Snacks")

    def test_create_duplicate_name(self) -> None:
        payload = {"company": str(self.company.pk), "name": "Parent"}
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_parent_company(self) -> None:
        foreign_parent = Category.objects.create(
            company=self.other_company, name="Foreign"
        )
        payload = {
            "company": str(self.company.pk),
            "name": "InvalidParent",
            "parent_category": str(foreign_parent.pk),
        }
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # 更新
    def test_update_name(self) -> None:
        url = self.detail_url(self.child)
        response = self.client.patch(url, {"name": "ChildRenamed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.child.refresh_from_db()
        self.assertEqual(self.child.name, "ChildRenamed")

    def test_update_circular_reference(self) -> None:
        url = self.detail_url(self.parent)
        response = self.client.patch(
            url, {"parent_category": str(self.child.pk)}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # 削除
    def test_delete(self) -> None:
        url = self.detail_url(self.child)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
