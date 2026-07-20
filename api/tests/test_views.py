import uuid

from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Category, Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="テスト会社")
        self.category = Category.objects.create(company=self.company, name="本")
        self.category2 = Category.objects.create(company=self.company, name="文房具")
        self.category3 = Category.objects.create(company=self.company, name="食品")
        self.list_url = "/api/categories/"
        self.detail_url = f"/api/categories/{self.category.id}/"

    def test_list(self):
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), Category.objects.count())

    def test_retrieve(self):
        res = self.client.get(self.detail_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["id"], str(self.category.id))
        self.assertEqual(res.data["name"], "本")

    def test_retrieve_nonexistent_returns_404(self):
        res = self.client.get(f"/api/categories/{uuid.uuid4()}/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_malformed_id_returns_404(self):
        res = self.client.get("/api/categories/hoge/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_create(self):
        before = Category.objects.count()
        payload = {"company": str(self.company.id), "name": "雑誌"}
        res = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), before + 1)
        self.assertEqual(res.data["name"], "雑誌")

    def test_create_duplicate_returns_400(self):
        before = Category.objects.count()
        payload = {"company": str(self.company.id), "name": "本"}
        res = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", res.data)
        self.assertEqual(Category.objects.count(), before)

    def test_create_missing_name_returns_400(self):
        before = Category.objects.count()
        payload = {"company": str(self.company.id)}
        res = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", res.data)
        self.assertEqual(Category.objects.count(), before)

    def test_update(self):
        res = self.client.patch(self.detail_url, {"name": "書籍"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "書籍")

    def test_update_duplicate_name_returns_400(self):
        detail_url2 = f"/api/categories/{self.category2.id}/"
        res = self.client.patch(detail_url2, {"name": "本"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", res.data)
        self.category2.refresh_from_db()
        self.assertEqual(self.category2.name, "文房具")

    def test_update_same_name_ok(self):
        res = self.client.patch(self.detail_url, {"name": "本"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_self_parent_returns_400(self):
        res = self.client.patch(
            self.detail_url, {"parent_category": str(self.category.id)}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", res.data)

    def test_update_valid_parent_ok(self):
        res = self.client.patch(
            self.detail_url, {"parent_category": str(self.category2.id)}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.parent_category_id, self.category2.id)

    def test_update_cycle_returns_400(self):
        self.category2.parent_category = self.category
        self.category2.save()
        res = self.client.patch(
            self.detail_url, {"parent_category": str(self.category2.id)}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", res.data)

    def test_destroy(self):
        before = Category.objects.count()
        res = self.client.delete(self.detail_url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), before - 1)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())
