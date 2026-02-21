import uuid
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from ..models.company import Company
from ..models.category import Category

class CategoryViewTests(APITestCase):
    """カテゴリAPIのテスト"""
    API_URL_CATEGORY_LIST = "api:category-list"
    API_URL_CATEGORY_DETAIL = "api:category-detail"
    
    def setUp(self):
        """テストデータの準備"""
        self.client = APIClient()
        self.company = Company.objects.create(name="テスト企業")
        self.another_company = Company.objects.create(name="テスト企業2")
        self.root1 = Category.objects.create(
            company=self.company,
            name="カテゴリ1",
            parent_category=None
        )
        self.root2 = Category.objects.create(
            company=self.company,
            name="カテゴリ2",
            parent_category=None
        )
        self.child1 = Category.objects.create(
            company=self.company,
            name="子カテゴリ1",
            parent_category=self.root1
        )
        self.child2 = Category.objects.create(
            company=self.another_company,
            name="子カテゴリ2",
            parent_category=None
        )

    def test_list(self):
        """カテゴリ一覧の取得テスト"""
        url = reverse(self.API_URL_CATEGORY_LIST)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    def test_list_zero(self):
        """カテゴリ一覧の0件での取得テスト"""
        self.root1.delete()
        self.root2.delete()
        self.child1.delete()
        self.child2.delete()

        url = reverse(self.API_URL_CATEGORY_LIST)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_retrieve(self):
        """特定のカテゴリの取得テスト"""
        url = reverse(self.API_URL_CATEGORY_DETAIL, kwargs={"pk": self.root1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "カテゴリ1")

    def test_retrieve_not_found(self):
        """取得対象が存在しない"""
        url = reverse(self.API_URL_CATEGORY_DETAIL, kwargs={"pk": uuid.uuid4})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    
    def test_create_without_parent(self):
        """親カテゴリ無しのカテゴリの作成テスト"""
        url = reverse(self.API_URL_CATEGORY_LIST)
        data = {
            "company": str(self.company.id),
            "name": "新カテゴリ",
            "parent_category": None
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 5)
    
    def test_create_with_parent(self):
        """親カテゴリ付きのカテゴリ作成テスト"""
        url = reverse(self.API_URL_CATEGORY_LIST)
        data = {
            "company": str(self.company.id),
            "name": "新子カテゴリ",
            "parent_category": str(self.root1.id)
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 5)
    
    def test_update(self):
        """カテゴリの更新テスト"""
        url = reverse(self.API_URL_CATEGORY_DETAIL, kwargs={"pk": self.root1.pk})
        data = {
            "company": str(self.company.id),
            "name": "カテゴリ1（更新）",
            "parent_category": None
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.root1.refresh_from_db()
        self.assertEqual(response.data["name"], "カテゴリ1（更新）")
    
    def test_update_not_found(self):
        """カテゴリの更新テスト"""
        url = reverse(self.API_URL_CATEGORY_DETAIL, kwargs={"pk": uuid.uuid4})
        data = {
            "company": str(self.company.id),
            "name": "カテゴリ1（更新）",
            "parent_category": None
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_partial_update(self):
        """カテゴリの部分更新テスト"""
        url = reverse(self.API_URL_CATEGORY_DETAIL, kwargs={"pk": self.root1.pk})
        data = {"name": "カテゴリ1（部分更新）"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.root1.refresh_from_db()
        self.assertEqual(response.data["name"], "カテゴリ1（部分更新）")

    def test_partial_update_not_found(self):
        """カテゴリの部分更新テスト"""
        url = reverse(self.API_URL_CATEGORY_DETAIL, kwargs={"pk": uuid.uuid4})
        data = {"name": "カテゴリ1（部分更新）"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_destroy_without_children(self):
        """子を持たないカテゴリの削除テスト"""
        url = reverse(self.API_URL_CATEGORY_DETAIL, kwargs={"pk": self.child1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 3)
    
    def test_destroy_with_children(self):
        """子を持つカテゴリの削除テスト（削除可能、子のparent_categoryはnullになる）"""
        url = reverse(self.API_URL_CATEGORY_DETAIL, kwargs={"pk": self.root1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 3)  # root2とchild1が残る
        # child1の親がnullになっていることを確認
        self.child1.refresh_from_db()
        self.assertIsNone(self.child1.parent_category)
        
        # 削除されたことを確認
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_destroy_not_found(self):
        """削除対象が存在しない"""
        url = reverse(self.API_URL_CATEGORY_DETAIL, kwargs={"pk": uuid.uuid4})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_validation_name_is_none(self):
        """ 名前に入力がなければエラー（None） """
        url = reverse(self.API_URL_CATEGORY_LIST)
        data = {
            "company": str(self.company.id),
            "name": None,
            "parent_category": None
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_validation_name_is_blank(self):
        """ 名前に入力がなければエラー（空文字） """
        url = reverse(self.API_URL_CATEGORY_LIST)
        data = {
            "company": str(self.company.id),
            "name": "",
            "parent_category": None
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_validation_name_is_space(self):
        """ 名前に入力がなければエラー（スペース） """
        url = reverse(self.API_URL_CATEGORY_LIST)
        data = {
            "company": str(self.company.id),
            "name": " ",
            "parent_category": None
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_validation_name_over_maxlength_255(self):
        """ 名前が255文字ちょうどはエラーとしない（境界値） """
        url = reverse(self.API_URL_CATEGORY_LIST)
        data = {
            "company": str(self.company.id),
            "name": "あ" * 255,
            "parent_category": None
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 5)

    def test_create_validation_name_over_maxlength_256(self):
        """ 名前が255文字を超えるとエラー（境界値超過） """
        url = reverse(self.API_URL_CATEGORY_LIST)
        data = {
            "company": str(self.company.id),
            "name": "あ" * 256,
            "parent_category": None
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_validation_multiple_conditions_under_same_company(self):
        """ 親カテゴリが指定されている場合、同じ企業に属してなければエラー """
        url = reverse(self.API_URL_CATEGORY_LIST)
        data = {
            "company": str(self.company.id),
            "name": "同一企業カテゴリ",
            "parent_category": str(self.child2.id)
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_validation_multiple_conditions_same_name(self):
        """ 企業とカテゴリ名が同じであればエラー """
        url = reverse(self.API_URL_CATEGORY_LIST)
        data = {
            "company": str(self.root1.company.id),
            "name": self.root1.name,
            "parent_category": None
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



    def test_update_validation_name_is_none(self):
        """ 名前に入力がなければエラー（None） """
        url = reverse(self.API_URL_CATEGORY_DETAIL, kwargs={"pk": self.root1.pk})
        data = {
            "company": str(self.root1.company.id),
            "name": None,
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_validation_name_is_blank(self):
        """ 名前に入力がなければエラー（空文字） """
        url = reverse(self.API_URL_CATEGORY_DETAIL, kwargs={"pk": self.root1.pk})
        data = {
            "company": str(self.root1.company.id),
            "name": "",
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_validation_name_is_space(self):
        """ 名前に入力がなければエラー（スペース） """
        url = reverse(self.API_URL_CATEGORY_DETAIL, kwargs={"pk": self.root1.pk})
        data = {
            "company": str(self.root1.company.id),
            "name": " ",
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_validation_name_over_maxlength_255(self):
        """ 名前が255文字ちょうどはエラーとしない（境界値） """
        url = reverse(self.API_URL_CATEGORY_DETAIL, kwargs={"pk": self.root1.pk})
        data = {
            "company": str(self.root1.company.id),
            "name": "あ" * 255,
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data["name"], "カテゴリ1")

    def test_update_validation_name_over_maxlength_256(self):
        """ 名前が255文字を超えるとエラー（境界値超過） """
        url = reverse(self.API_URL_CATEGORY_DETAIL, kwargs={"pk": self.root1.pk})
        data = {
            "company": str(self.root1.company.id),
            "name": "あ" * 256,
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_validation_parent_category_same_id(self):
        """ 自分自身を親カテゴリに設定するとエラー """
        url = reverse(self.API_URL_CATEGORY_DETAIL, kwargs={"pk": self.root1.pk})
        data = {
            "company": str(self.root1.company.id),
            "name": "カテゴリ1（更新）",
            "parent_category": str(self.root1.id)
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_validation_parent_category_circular_reference(self):
        """ 循環参照が発生するとエラー """
        url = reverse(self.API_URL_CATEGORY_DETAIL, kwargs={"pk": self.root1.pk})
        data = {
            "company": str(self.root1.company.id),
            "name": "カテゴリ1（更新）",
            "parent_category": str(self.child1.id)
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_validation_multiple_conditions_under_same_company_1(self):
        """ 親カテゴリが同一企業でない場合はエラー（companyの更新あり） """
        url = reverse(self.API_URL_CATEGORY_DETAIL, kwargs={"pk": self.root1.pk})
        data = {
            "company": str(self.root1.company.id),
            "name": "カテゴリ1（更新-同一企業）",
            "parent_category": str(self.child2.id)
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_validation_multiple_conditions_under_same_company_2(self):
        """ 親カテゴリが同一企業でない場合はエラー（companyの更新なし） """
        url = reverse(self.API_URL_CATEGORY_DETAIL, kwargs={"pk": self.root1.pk})
        data = {
            "company": str(self.root1.company.id),
            "name": "カテゴリ1（更新-同一企業）",
            "parent_category": str(self.child2.id)
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_validation_multiple_conditions_same_name(self):
        """ 企業とカテゴリ名の組み合わせがユニークでなければエラー """
        url = reverse(self.API_URL_CATEGORY_DETAIL, kwargs={"pk": self.root1.pk})
        data = {
            "company": str(self.root2.company.id),
            "name": self.root2.name
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



    def test_partial_update_validation_name_is_none(self):
        """ 名前に入力がなければエラー（None） """
        url = reverse(self.API_URL_CATEGORY_DETAIL, kwargs={"pk": self.root1.pk})
        data = {
            "name": None,
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_update_validation_name_is_blank(self):
        """ 名前に入力がなければエラー（空文字） """
        url = reverse(self.API_URL_CATEGORY_DETAIL, kwargs={"pk": self.root1.pk})
        data = {
            "name": "",
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_update_validation_name_is_space(self):
        """ 名前に入力がなければエラー（スペース） """
        url = reverse(self.API_URL_CATEGORY_DETAIL, kwargs={"pk": self.root1.pk})
        data = {
            "name": " ",
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_update_validation_name_over_maxlength_255(self):
        """ 名前が255文字ちょうどはエラーとしない（境界値） """
        url = reverse(self.API_URL_CATEGORY_DETAIL, kwargs={"pk": self.root1.pk})
        data = {
            "name": "あ" * 255,
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data["name"], "カテゴリ1")

    def test_partial_update_validation_name_over_maxlength_256(self):
        """ 名前が255文字を超えるとエラー（境界値超過） """
        url = reverse(self.API_URL_CATEGORY_DETAIL, kwargs={"pk": self.root1.pk})
        data = {
            "name": "あ" * 256,
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_update_validation_parent_category_same_id(self):
        """ 自分自身を親カテゴリに設定するとエラー """
        url = reverse(self.API_URL_CATEGORY_DETAIL, kwargs={"pk": self.root1.pk})
        data = {
            "name": "カテゴリ1（更新）",
            "parent_category": str(self.root1.id)
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_update_validation_parent_category_circular_reference(self):
        """ 循環参照が発生するとエラー """
        url = reverse(self.API_URL_CATEGORY_DETAIL, kwargs={"pk": self.root1.pk})
        data = {
            "name": "カテゴリ1（更新）",
            "parent_category": str(self.child1.id)
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_update_validation_multiple_conditions_under_same_company_1(self):
        """ 親カテゴリが同一企業でない場合はエラー（companyの更新あり） """
        url = reverse(self.API_URL_CATEGORY_DETAIL, kwargs={"pk": self.root1.pk})
        data = {
            "company": str(self.root1.company.id),
            "name": "カテゴリ1（更新-同一企業）",
            "parent_category": str(self.child2.id)
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_update_validation_multiple_conditions_under_same_company_2(self):
        """ 親カテゴリが同一企業でない場合はエラー（companyの更新なし） """
        url = reverse(self.API_URL_CATEGORY_DETAIL, kwargs={"pk": self.root1.pk})
        data = {
            "name": "カテゴリ1（更新-同一企業）",
            "parent_category": str(self.child2.id)
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_update_validation_multiple_conditions_same_name(self):
        """ 企業とカテゴリ名の組み合わせがユニークでなければエラー """
        url = reverse(self.API_URL_CATEGORY_DETAIL, kwargs={"pk": self.root1.pk})
        data = {
            "company": str(self.root2.company.id),
            "name": self.root2.name
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
