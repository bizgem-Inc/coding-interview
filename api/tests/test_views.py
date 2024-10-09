from ..models import Category, Company
from django.urls import reverse
from rest_framework.test import APITestCase


class CategoryViewTests(APITestCase):
    fixtures = ["test_company", "test_category"]

    def test_list(self):
        """ fixtureのカテゴリ2つが表示される"""
        url = reverse("category-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_retrieve(self):
        """ カテゴリが表示される """
        target = Category.objects.get(name="test category1")
        url = reverse("category-detail", kwargs={"pk": target.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], target.name)

    def test_retrieve_missing_id(self):
        """ 存在しないカテゴリIDでは404が返る """
        url = reverse("category-detail", kwargs={"pk": "not_found"})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_create(self):
        """ カテゴリが作成できる """
        url = reverse("category-list")
        company = Company.objects.get(name="test company1")
        before_count = Category.objects.count()

        response = self.client.post(
            url, {"company": company.id, "name": "test category"})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Category.objects.count(), before_count+1)

    def test_create_parameter_long(self):
        """ カテゴリの名前は255文字まで """
        url = reverse("category-list")
        company = Company.objects.get(name="test company1")
        before_count = Category.objects.count()

        response = self.client.post(
            url, {"company": company.id, "name": "t"*255})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Category.objects.count(), before_count+1)

    def test_create_parameter_too_long(self):
        """ カテゴリの名前は255文字まで """
        url = reverse("category-list")
        company = Company.objects.get(name="test company1")
        before_count = Category.objects.count()

        response = self.client.post(
            url, {"company": company.id, "name": "t"*256})

        self.assertEqual(Category.objects.count(), before_count)
        self.assertEqual(response.status_code, 400)

    def test_create_missiing_parrameter(self):
        """ パラメータが足りないとカテゴリが作成できない """
        url = reverse("category-list")
        before_count = Category.objects.count()

        response = self.client.post(
            url, {"name": "test category"})

        self.assertEqual(Category.objects.count(), before_count)
        self.assertEqual(response.status_code, 400)

    def test_create_duplicate_parameter(self):
        """ 名前と会社の組はユニークである必要がある """
        target = Category.objects.get(name="test category1")
        url = reverse("category-list")
        before_count = Category.objects.count()

        response = self.client.post(
            url, {"name": target.name, "company": target.company.id})

        self.assertEqual(Category.objects.count(), before_count)
        self.assertEqual(response.status_code, 400)

    # update
    def test_update(self):
        """ カテゴリが更新できる """
        target = Category.objects.get(name="test category1")
        company = Company.objects.get(name="test company2")
        url = reverse("category-detail", kwargs={"pk": target.id})

        response = self.client.put(
            url, {"company": company.id, "name": "change category1", "parent_category": target.parent_category.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "change category1")

    def test_update_minimum_parameter(self):
        """ カテゴリは名前と会社だけあれば更新できる """
        target = Category.objects.get(name="test category1")
        company = Company.objects.get(name="test company2")
        url = reverse("category-detail", kwargs={"pk": target.id})

        response = self.client.put(
            url, {"company": company.id, "name": "change category1"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "change category1")
        self.assertEqual(
            response.data["parent_category"], target.parent_category.id)

    def test_update_missing_parameter(self):
        """ カテゴリ更新時には名前、会社は必須 """
        target = Category.objects.get(name="test category1")
        url = reverse("category-detail", kwargs={"pk": target.id})

        response = self.client.put(
            url, {"name": "change category1", "parent_category": target.parent_category.id})

        self.assertEqual(response.status_code, 400)

    def test_update_duplicate_parameter(self):
        """ 名前と会社の組はユニークである必要がある """
        target = Category.objects.get(name="test category1")
        value_target = Category.objects.get(name="test category2")
        url = reverse("category-detail", kwargs={"pk": target.id})

        response = self.client.put(
            url, {"name": value_target.name, "company": value_target.company})

        self.assertEqual(response.status_code, 400)

    # destroy
    def test_destroy(self):
        """ カテゴリが削除できる """
        target = Category.objects.get(name="test category1")
        before_count = Category.objects.count()
        url = reverse("category-detail", kwargs={"pk": target.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Category.objects.count(), before_count-1)

    def test_destroy_missing_id(self):
        """ 存在しないカテゴリIDは削除できない """
        before_count = Category.objects.count()
        url = reverse("category-detail", kwargs={"pk": "not_found"})

        response = self.client.delete(url)

        self.assertEqual(Category.objects.count(), before_count)
        self.assertEqual(response.status_code, 404)
