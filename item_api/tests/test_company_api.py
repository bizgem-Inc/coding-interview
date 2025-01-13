import uuid
from typing import Any, Callable
from uuid import UUID

from rest_framework import status
from rest_framework.test import APITestCase

from item_api.exception import uuid_error_message
from item_api.exception.custom_exceptions import PutNotAllowedException
from item_api.models import Company
from item_api.serializers.company import CompanySerializer
from item_api.tests import convert_model_to_company_list


class CompanyAPITestCase(APITestCase):
    _url = "/api/companies"

    def _with_path_parameter(self, company_id: UUID) -> str:
        return f"{self._url}/{company_id.hex}"

    def test_post(self):
        """
        企業を作成できること
        """
        given = "test_for_list"
        response = self.client.post(self._url, format="json", data={"name": given})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        actual = CompanySerializer(Company.objects.get(pk=response.data["id"])).data

        self.assertEqual(response.data, actual)
        self.assertEqual(actual["name"], given)

    def test_post_for_bad_request(self):
        """
        企業名を指定しないので Bad Request になること
        """
        response = self.client.post(self._url, format="json", data={"name": None})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "企業名は必須項目です")

    def test_list(self):
        """
        企業のリストを取得できること
        デフォルトのページネーションが想定通りに動作していること
        """
        self._paging_test(
            item_count=5,
            execute_request=lambda: self.client.get(self._url, format="json"),
        )

    def test_list_paging_10(self):
        """
        企業のリストを取得できること
        10 行のページネーションが想定通りに動作していること
        """
        self._paging_test(
            item_count=10,
            execute_request=lambda: self.client.get(
                f"{self._url}?page_size=10", format="json"
            ),
        )

    def _paging_test(self, item_count: int, execute_request: Callable[[], Any]):
        Company.objects.all().delete()
        expected = []
        for index in range(20):
            given = f"test_for_list{index}"
            company = Company(name=given)
            company.save()
            if index >= 20 - item_count:
                expected.append(company)

        # expected = Company.objects.filter(id__in=expected_ids)
        response = execute_request()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(len(results), item_count)
        # ソートが降順で行われていること
        self.assertListEqual(
            list(results), convert_model_to_company_list(expected[::-1])
        )

    def test_retrieve(self):
        """
        企業を 1 つ取得できること
        """
        Company.objects.all().delete()
        given = "test_for_list"
        expected = Company(name=given)
        expected.save()

        response = self.client.get(
            self._with_path_parameter(expected.id), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, CompanySerializer(expected).data)

    def test_retrieve_not_found(self):
        """
        企業が存在しない場合は 404 を返すこと
        """
        Company.objects.all().delete()

        response = self.client.get(
            self._with_path_parameter(uuid.uuid4()), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["message"], "指定された企業が存在しません")

    def test_update_name(self):
        """
        企業の名称を変更できること
        """
        test_data = Company(name="before")
        test_data.save()

        given = "after"
        response = self.client.patch(
            self._with_path_parameter(test_data.id), format="json", data={"name": given}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = Company.objects.get(pk=test_data.id)
        self.assertEqual(expected.name, given)
        self.assertEqual(response.data, CompanySerializer(expected).data)

    def test_update_invalid_uuid_format(self):
        """
        UUID の形式が不正である場合はエラーになること
        """
        given = "after"
        response = self.client.patch(
            f"{self._url}/1", format="json", data={"name": given}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], uuid_error_message)

    def test_update_not_found(self):
        """
        存在しない企業は 404 が返ること
        """
        given = "after"
        response = self.client.patch(
            self._with_path_parameter(uuid.uuid4()), format="json", data={"name": given}
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["message"], "指定された企業が存在しません")

    def test_patch_invalid_request(self):
        """
        企業名を指定しないので Bad Request になること
        """
        test_data = Company(name="test")
        test_data.save()
        response = self.client.patch(
            self._with_path_parameter(test_data.id), format="json", data={"name": None}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "企業名は必須項目です")

    def test_delete_company(self):
        """
        企業を削除できること
        """
        test_data = Company(name="will delete")
        test_data.save()

        response = self.client.delete(
            self._with_path_parameter(test_data.id), format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Company.DoesNotExist):
            Company.objects.get(pk=test_data.id)

    def test_delete_invalid_uuid_format(self):
        """
        削除時 UUID の形式が不正でエラーになること
        """
        given = "after"
        response = self.client.delete(
            f"{self._url}/1", format="json", data={"name": given}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], uuid_error_message)

    def test_delete_not_found(self):
        """
        存在しない企業は 404 が返ること
        """
        given = "after"
        response = self.client.delete(
            self._with_path_parameter(uuid.uuid4()), format="json", data={"name": given}
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_not_allowed(self):
        """
        PUT は許可されていないこと
        """
        given = "after"
        response = self.client.put(
            self._with_path_parameter(uuid.uuid4()), format="json", data={"name": given}
        )

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(
            response.data["message"], PutNotAllowedException().default_detail
        )
