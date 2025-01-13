import uuid
from typing import Optional, Dict, Callable, Any, List

from rest_framework import status
from rest_framework.test import APITestCase

from item_api.exception import uuid_error_message
from item_api.exception.custom_exceptions import NoUpdateParameterException
from item_api.models import Category, Company
from item_api.serializers.category import CategorySerializer
from item_api.tests import convert_model_to_company_list, convert_model_to_category_list, convert_to_category_dict
from item_api.util import uuid_of
from item_api.views.category import format_response_body_by_dict


class CategoryAPITestCase(APITestCase):
    _url = '/api/categories'

    @classmethod
    def setUpTestData(cls):
        """
        テスト前に対象外の企業を作成します
        """
        for index in range(0, 20):
            company = Company(
                name=f'test {index}'
            )
            company.save()

    def _with_path_parameter(self, category_id: uuid.UUID) -> str:
        return f'{self._url}/{category_id.hex}'

    def _create_parameter(self, name: Optional[str] = None, parent_category_id: Optional[str] = None,
                          company: Optional[str] = None) -> Dict[str, str]:
        return {
            'name': name,
            'parent_category': parent_category_id,
            'company': company,
        }

    def _test_name(self) -> str:
        return uuid.uuid4().hex[0:10]

    def test_post(self):
        """
        カテゴリを作成できること
        """
        company = Company(
            name=self._test_name()
        )
        company.save()

        given = self._create_parameter(
            name=self._test_name(),
            company=company.id,
        )

        response = self.client.post(self._url, format='json', data=given)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        actual = CategorySerializer(Category.objects.get(pk=response.data['id'])).data

        self.assertEquals(response.data, format_response_body_by_dict(actual))
        self.assertEquals(actual['name'], given['name'])
        db_actual = Category.objects.get(pk=actual['id'])
        self.assertEquals(db_actual.name, given['name'])
        self.assertEquals(db_actual.parent_category, None)
        self.assertEquals(db_actual.company.id, company.id)

        # 親のカテゴリを指定できること
        given_with_parent = self._create_parameter(
            name=self._test_name(),
            company=company.id,
            parent_category_id=given['parent_category']
        )
        response_with_parent = self.client.post(self._url, format='json', data=given_with_parent)
        self.assertEquals(response_with_parent.status_code, status.HTTP_201_CREATED)
        actual_with_parent = CategorySerializer(Category.objects.get(pk=response_with_parent.data['id'])).data
        self.assertEquals(response_with_parent.data, format_response_body_by_dict(actual_with_parent))
        self.assertEquals(actual_with_parent['name'], given_with_parent['name'])
        db_actual_with_parent = Category.objects.get(pk=actual_with_parent['id'])
        self.assertEquals(db_actual_with_parent.name, given_with_parent['name'])
        self.assertEquals(db_actual_with_parent.parent_category, db_actual.parent_category)
        self.assertEquals(db_actual_with_parent.company.id, company.id)

    def test_post_for_bad_request_name(self):
        """
        カテゴリ名を指定しないので Bad Request になること
        """
        response = self.client.post(self._url, format='json', data={'company': uuid.uuid4().hex, 'name': None})
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(response.data['message'], 'カテゴリ名を指定してください')


    def test_post_for_bad_request_company(self):
        """
        企業IDを指定しないので Bad Request になること
        """
        response = self.client.post(self._url, format='json', data={'company': None, 'name': 'name'})
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(response.data['message'], '企業IDを指定してください')

    def test_post_for_bad_invalid_parent_id(self):
        """
        存在しない親カテゴリIDを指定して失敗すること
        """
        company = Company(
            name=self._test_name()
        )
        company.save()

        parent_category=uuid.uuid4()
        given = self._create_parameter(
            name=self._test_name(),
            company=company.id,
            parent_category_id=parent_category.hex,
        )

        response = self.client.post(self._url, format='json', data=given)
        self.assertEquals(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEquals(response.data['message'], f'親カテゴリ[{str(parent_category)}]は存在していません')

    def test_post_for_bad_different_company_parent_id(self):
        """
        別企業の親カテゴリIDを指定して失敗すること
        """
        company1 = Company(
            name=self._test_name()
        )
        company1.save()
        parent_category = Category(
            name=self._test_name(),
            company=company1,
        )
        parent_category.save()

        company2 = Company(
            name=self._test_name()
        )
        company2.save()
        given = self._create_parameter(
            name=self._test_name(),
            company=company2.id,
            parent_category_id=parent_category.id.hex,
        )

        response = self.client.post(self._url, format='json', data=given)
        self.assertEquals(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEquals(response.data['message'], f'指定した親カテゴリidは[{str(company2.id)}]のカテゴリではありません')

    def test_list_paging(self):
        """
        カテゴリリストを取得できること
        ページネーションが想定通りに動作していること
        """
        company = Company(name=self._test_name())
        company.save()
        parent = Category(company=company, name='p' + self._test_name())
        parent.save()
        expected: List[Category] = []
        for index in range(20):
            given = f'test_for_list{index}'
            category = Category(
                name=given,
                company=company,
                parent_category=None if index % 2 == 0 else parent
            )
            category.save()
            if index >= 18:
                expected.append(category)

        # expected = Category.objects.filter(id__in=expected_ids)
        response = self.client.get(f'{self._url}?page_size=2')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEquals(len(results), 2)
        # ソートが降順で行われていること
        self.assertListEqual(list(results), convert_model_to_category_list(expected[::-1]))

    def test_list_query_by_company_id(self):
        """
        企業ID でカテゴリリストを取得できること
        """
        company1 = Company(name=self._test_name())
        company1.save()
        company2 = Company(name=self._test_name())
        company2.save()

        expected: List[Category] = []
        test_count = 6
        for index in range(test_count):
            given = f'test_for_list{index}'
            category = Category(
                name=given,
                company=company1 if index % 2 == 0 else company2,
            )
            category.save()
            if index % 2 == 0:
                expected.append(category)

        response = self.client.get(f'{self._url}?company={str(company2.id)}')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEquals(len(results), test_count / 2)
        for result in results:
            self.assertEquals(result['company'], str(company2.id))

    def test_list_query_by_category_name(self):
        """
        カテゴリリストを名前で取得できること
        """
        company = Company(name=self._test_name())
        company.save()

        expected: List[Category] = []
        test_count = 6
        target_name = 'target'
        for index in range(test_count):
            category = Category(
                name=target_name + self._test_name() if index % 2 == 0 else self._test_name(),
                company=company,
            )
            category.save()
            if index % 2 == 0:
                expected.append(category)

        response = self.client.get(f'{self._url}?name={target_name}')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEquals(len(results), test_count / 2)
        for result in results:
            self.assertEquals(target_name in result['name'], True)

    def test_retrieve(self):
        """
        カテゴリを 1 つ取得できること
        """
        company = Company(name=self._test_name())
        company.save()
        expected = Category(name=self._test_name(), company=company)
        expected.save()

        response = self.client.get(self._with_path_parameter(expected.id), format='json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data, convert_to_category_dict(expected))

    def test_retrieve_not_found(self):
        """
        カテゴリが存在しない場合は 404 を返すこと
        """
        response = self.client.get(self._with_path_parameter(uuid.uuid4()), format='json')
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEquals(response.data['message'], '指定されたカテゴリが存在しません')

    def test_patch_name(self):
        """
        カテゴリの名称を変更できること
        """
        company = Company(name=self._test_name())
        company.save()
        test_data = Category(company=company, name="before")
        test_data.save()

        given = 'after'
        response = self.client.patch(self._with_path_parameter(test_data.id), format='json', data={"name": given})

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        expected = Category.objects.get(pk=test_data.id)
        self.assertEquals(expected.name, given)
        self.assertEquals(response.data, convert_to_category_dict(expected))

    def test_patch_parent_category(self):
        """
        カテゴリの親カテゴリを変更できること
        """
        company = Company(name=self._test_name())
        company.save()
        parent1 = Category(company=company, name=self._test_name())
        parent1.save()
        test_data = Category(company=company, name=self._test_name(), parent_category=parent1)
        test_data.save()

        parent2 = Category(company=company, name=self._test_name())
        parent2.save()

        response = self.client.patch(self._with_path_parameter(test_data.id), format='json',
                                     data={"parent_category": str(parent2.id)})

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        expected = Category.objects.get(pk=test_data.id)
        self.assertEquals(expected.parent_category.id, parent2.id)
        self.assertEquals(response.data, convert_to_category_dict(expected))

    def test_patch_company(self):
        """
        カテゴリの会社を変更できること
        """
        company_before = Company(name=self._test_name())
        company_before.save()
        test_data = Category(company=company_before, name=self._test_name())
        test_data.save()

        company_after = Company(name=self._test_name())
        company_after.save()

        response = self.client.patch(self._with_path_parameter(test_data.id), format='json',
                                     data={"company": str(company_after.id)})

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        expected = Category.objects.get(pk=test_data.id)
        self.assertEquals(expected.company.id, company_after.id)
        self.assertEquals(response.data, convert_to_category_dict(expected))

    def test_patch_same_name_in_difference_company(self):
        """
        別会社で同一の名前のカテゴリで登録・変更できること
        """
        category_name = self._test_name()
        company_1 = Company(name=self._test_name())
        company_1.save()
        test_data = Category(company=company_1, name=category_name)
        test_data.save()

        company_2 = Company(name=self._test_name())
        company_2.save()

        created_response = self.client.post(self._url, format='json',
                                    data=self._create_parameter(
                                        name=category_name,
                                        company=str(company_2.id),
                                    ))

        self.assertEquals(created_response.status_code, status.HTTP_201_CREATED)

        after_category_name = self._test_name()
        patched1 = self.client.patch(self._with_path_parameter(test_data.id), format='json',
                                     data={"name" : after_category_name}
                                     )

        self.assertEquals(patched1.status_code, status.HTTP_200_OK)
        patched2 = self.client.patch(self._with_path_parameter(uuid.UUID(created_response.data['id'])), format='json',
                                     data={"name" : after_category_name}
                                     )
        self.assertEquals(patched2.status_code, status.HTTP_200_OK)


    def test_put_change_all_value(self):
        """
        PUT で更新できること
        """
        company = Company(name=self._test_name())
        company.save()
        parent1 = Category(company=company, name=self._test_name())
        parent1.save()
        parent2 = Category(company=company, name=self._test_name())
        parent2.save()
        test_data = Category(company=company, name=self._test_name(), parent_category=parent1)
        test_data.save()
        given = self._create_parameter(
            name=self._test_name(),
            company=company.id.hex,
            parent_category_id=parent2.id.hex
        )
        response = self.client.put(self._with_path_parameter(test_data.id),
                  format='json',
                    data=given)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        expected = Category.objects.get(pk=test_data.id)
        self.assertEquals(response.data, convert_to_category_dict(expected))


    def test_put_no_name(self):
        """
        カテゴリ名を指定しないで PUT するので失敗すること
        """
        company = Company(name=self._test_name())
        company.save()
        category = Category(company=company, name=self._test_name())
        category.save()
        given = self._create_parameter(
            name=None,
            company=company.id.hex,
            parent_category_id=category.id.hex
        )
        response = self.client.put(f'{self._with_path_parameter(category.id)}', format='json', data= given)

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(response.data['message'], NoUpdateParameterException("カテゴリ名").default_detail)

    def test_put_no_company(self):
        """
        企業を指定しないで PUT するので失敗すること
        """
        company = Company(name=self._test_name())
        company.save()
        category = Category(company=company, name=self._test_name())
        category.save()
        given = self._create_parameter(
            name=self._test_name(),
            company=None,
            parent_category_id=category.id.hex
        )
        response = self.client.put(f'{self._with_path_parameter(category.id)}', format='json', data= given)

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(response.data['message'], NoUpdateParameterException("企業ID").default_detail)

    def test_put_parent_null(self):
        """
        親カテゴリを NULL にセットできること
        """
        company = Company(name=self._test_name())
        company.save()
        parent = Category(company=company, name=self._test_name())
        parent.save()
        category = Category(company=company, name=self._test_name(), parent_category=parent)
        category.save()

        before = Category.objects.get(pk=category.id)
        self.assertEquals(before.parent_category, parent)

        given = self._create_parameter(
            name=self._test_name(),
            company=company.id.hex,
            parent_category_id=None
        )
        response = self.client.put(f'{self._with_path_parameter(category.id)}', format='json', data= given)

        self.assertEquals(response.status_code, status.HTTP_200_OK)

        after = Category.objects.get(pk=category.id)
        self.assertEquals(after.parent_category, None)


    def test_put_invalid_uuid_format(self):
        """
        UUID の形式が不正である場合はエラーになること
        """
        company = Company(name=self._test_name())
        company.save()
        parent1 = Category(company=company, name=self._test_name())
        parent1.save()
        given = self._create_parameter(
            name=self._test_name(),
            company=company.id.hex,
            parent_category_id=parent1.id.hex
        )
        response = self.client.put(f'{self._url}/1', format='json', data=given)

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(response.data['message'], uuid_error_message)


    def test_put_all_same(self):
        """
        すべてが同じ内容で更新する場合、名称が重複してエラーになること
        """
        company = Company(name=self._test_name())
        company.save()
        category = Category(company=company, name=self._test_name())
        category.save()
        given = self._create_parameter(
            name=category.name,
            company=company.id.hex,
            parent_category_id=category.id.hex
        )
        response = self.client.put(f'{self._with_path_parameter(category.id)}', format='json', data=given)

        self.assertEquals(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEquals(response.data['message'], f'{given["name"]}はすでに登録済みのカテゴリです')


    def test_patch_same_name(self):
        """
        名称を全く同じ名前で更新しようとすると、名称が重複してエラーになること
        """
        company = Company(name=self._test_name())
        company.save()
        category = Category(company=company, name=self._test_name())
        category.save()
        given = self._create_parameter(
            name=category.name,
            company=None,
            parent_category_id=None,
        )
        response = self.client.patch(f'{self._with_path_parameter(category.id)}', format='json', data=given)

        self.assertEquals(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEquals(response.data['message'], f'{given["name"]}はすでに登録済みのカテゴリです')

    def test_patch_invalid_uuid_format(self):
        """
        UUID の形式が不正である場合はエラーになること
        """
        given = 'after'
        response = self.client.patch(f'{self._url}/1', format='json', data={"name": given})

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(response.data['message'], uuid_error_message)

    def test_patch_not_found(self):
        """
        存在しないカテゴリは 404 が返ること
        """
        given = self._test_name()
        response = self.client.patch(self._with_path_parameter(uuid.uuid4()), format='json', data={"name": given})

        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEquals(response.data['message'], '指定されたカテゴリが存在しません')

    def test_patch_invalid_request(self):
        """
        パラメーターを指定しないので Bad Request になること
        """
        company = Company(name=self._test_name())
        company.save()
        test_data = Category(name=self._test_name(), company=company)
        test_data.save()
        response = self.client.patch(self._with_path_parameter(test_data.id), format='json', data={})
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(response.data['message'], 'カテゴリ名または企業IDまたは親カテゴリIDを指定してください')


    def test_delete_category(self):
        """
        カテゴリを削除できること
        """
        company = Company(name=self._test_name())
        company.save()
        test_data = Category(name=self._test_name(), company=company)
        test_data.save()

        response = self.client.delete(self._with_path_parameter(test_data.id), format='json')

        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Category.DoesNotExist):
            Category.objects.get(pk=test_data.id)

    def test_delete_parent_category(self):
        """
        親カテゴリにセットされたカテゴリを削除した場合、セットしている子カテゴリの親が NULL になること
        """
        company = Company(name=self._test_name())
        company.save()
        parent = Category(name=self._test_name(), company=company)
        parent.save()

        child = Category(name=self._test_name(), company=company, parent_category=parent)
        child.save()

        before = Category.objects.get(pk=child.id)
        self.assertEquals(before.parent_category.id, parent.id)

        response = self.client.delete(self._with_path_parameter(parent.id), format='json')

        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)

        after = Category.objects.get(pk=child.id)
        self.assertEquals(after.parent_category, None)

    def test_delete_invalid_uuid_format(self):
        """
        削除時 UUID の形式が不正でエラーになること
        """
        given = 'after'
        response = self.client.delete(f'{self._url}/1', format='json', data={"name": given})

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(response.data['message'], uuid_error_message)

    def test_delete_not_found(self):
        """
        存在しない企業は 404 が返ること
        """
        given = 'after'
        response = self.client.delete(self._with_path_parameter(uuid.uuid4()), format='json', data={"name": given})

        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)
