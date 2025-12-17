from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company

# 「カテゴリ」の深度の限界値を検査する。
from api.serializers.category import MAX_DEPTH

import logging
logger = logging.getLogger(__name__)

class CategoryViewTests(APITestCase):

    TARGET_URL = '/api/categories/'

    def setUp(self):
        # テスト全体で頻繁に使う「会社」を作成する
        for i in range(10):
            Company.objects.create(name=f"テスト会社{i}")

    def test_list(self):
        pass

    def test_retrieve(self):
        pass

    def test_create_category_001(self):
        """
        正常系: 1件の「会社」に対して、複数個のカテゴリを登録する
        """
        for i in range(4):
            payload = {
                "company": str(Company.objects.first().id),
                "name": f"カテゴリ{i}",
                "parent_category": None,
            }
            response = self.client.post(self.TARGET_URL, payload, format="json")
            self.assertEqual(response.status_code, 201)
        pass

    def test_create_category_002(self):
        """
        正常系: 複数個の「会社」に対して、1個のカテゴリを登録する
        """
        companies = list(Company.objects.all())
        for i in range(10):
            payload = {
                "company": companies[i].id,
                "name": f"カテゴリA",
                "parent_category": None,
            }
            response = self.client.post(self.TARGET_URL, payload, format="json")
            self.assertEqual(response.status_code, 201)
        pass

    def test_create_category_003(self):
        """
        正常系:
        10件の「会社」に対して、1個のカテゴリを登録する。
        このとき、特定の親「カテゴリ」を指定する。
        """
        companies = list(Company.objects.all())

        # (01) 親カテゴリを 1件だけ作成する
        payload = {
            "company": companies[0].id,
            "name": f"親カテゴリ",
            "parent_category": None,
        }
        response = self.client.post(self.TARGET_URL, payload, format="json")
        self.assertEqual(response.status_code, 201)

        # 親カテゴリ
        parent_category_id = response.data["id"]

        # (02) 上記(01)で作成した、1件の親カテゴリを指定して、子カテゴリの作成をする
        for i in range(10):
            payload = {
                "company": companies[i].id,
                "name": f"カテゴリ{i}",
                "parent_category": parent_category_id,
            }
            response = self.client.post(self.TARGET_URL, payload, format="json")
            self.assertEqual(response.status_code, 201)
        pass

    def test_create_category_004(self):
        """
        正常系:
        次のようにツリー上にカテゴリが作成されるように登録する。
        このとき、各カテゴリに関連付けられる「会社」は特定の1件とする。
        親カテゴリ
        `-- カテゴリ[0]
            `-- カテゴリ[1]
                `-- カテゴリ[2]
                    (略)
                    `-- カテゴリ[n]
        """
        companies = list(Company.objects.all())

        # (01) 親カテゴリを 1件だけ作成する
        payload = {
            "company": companies[0].id,
            "name": f"親カテゴリ",
            "parent_category": None,
        }
        response = self.client.post(self.TARGET_URL, payload, format="json")
        self.assertEqual(response.status_code, 201)

        parent_category_id = response.data["id"] # 親カテゴリ

        # (02) 上記(01)で作成した、1件の親カテゴリを指定して、子カテゴリの作成をする
        payload = {
            "company": companies[0].id,
            "name": f"カテゴリ0",
            "parent_category": parent_category_id,
        }
        response = self.client.post(self.TARGET_URL, payload, format="json")
        self.assertEqual(response.status_code, 201)
        parent_category_id = response.data["id"]

        # (03) 上記(02)のつづき
        for i in range(2,6):
#           logger.error(f"[{i}] ------------------------------------------")
#           logger.error(f"[{i}] parent_category_id => {parent_category_id}")
            payload = {
                "company": companies[0].id,
                "name": f"カテゴリ{i}",
                "parent_category": parent_category_id,
            }
            response = self.client.post(self.TARGET_URL, payload, format="json")
            self.assertEqual(response.status_code, 201)
            parent_category_id = response.data["id"]
#           logger.error(f"[{i}] parent_category_id => {parent_category_id}")
        pass

    def test_create_category_101(self):
        """
        異常系:
        すでに、指定の「企業ID」と「カテゴリ名」のペアが存在している場合に、
        ClientError(400)、かつ、所定のメッセージが表示されることを確認する。
        """
        # (01) 1件目の登録
        payload = {
            "company": str(Company.objects.first().id),
            "name": f"カテゴリ0",
            "parent_category": None,
        }
        response = self.client.post(self.TARGET_URL, payload, format="json")
        self.assertEqual(response.status_code, 201)

        # (02) 1件目の登録
        payload = {
            "company": str(Company.objects.first().id),
            "name": f"カテゴリ0",
            "parent_category": None,
        }
        response = self.client.post(self.TARGET_URL, payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            'すでに、指定の「企業ID」と「カテゴリ名」のペアが存在しています。',
            str(response.data)
        )

    def test_create_category_102(self):
        """
        異常系:
        次のように「カテゴリ」の深度の限界値を検査する。
        n=6 の場合は許容範囲`外`である。

              親カテゴリ <- 子カテゴリ1 <- 子カテゴリ2 <- (略) <- 子カテゴリn
        """
        companies = list(Company.objects.all())

        # (01) 親カテゴリを 1件だけ作成する
        payload = {
            "company": companies[0].id,
            "name": f"親カテゴリ",
            "parent_category": None,
        }
        response = self.client.post(self.TARGET_URL, payload, format="json")
        self.assertEqual(response.status_code, 201)

        parent_category_id = response.data["id"] # 親カテゴリ

        # (02) 上記(01)で作成した、1件の親カテゴリを指定して、子カテゴリの作成をする
        payload = {
            "company": companies[0].id,
            "name": f"カテゴリ0",
            "parent_category": parent_category_id,
        }
        response = self.client.post(self.TARGET_URL, payload, format="json")
        self.assertEqual(response.status_code, 201)
        parent_category_id = response.data["id"]

        # (03) 上記(02)のつづき
        for i in range(2,7):
#           logger.error(f"[{i}] ------------------------------------------")
#           logger.error(f"[{i}] parent_category_id => {parent_category_id}")
            payload = {
                "company": companies[0].id,
                "name": f"カテゴリ{i}",
                "parent_category": parent_category_id,
            }
            response = self.client.post(self.TARGET_URL, payload, format="json")
            if i < 6:
                self.assertEqual(response.status_code, 201)
                parent_category_id = response.data["id"]
            else:
                self.assertEqual(response.status_code, 400)
                self.assertIn(f"カテゴリ階層は最大{MAX_DEPTH}階層までにしてください", str(response.data))
#           logger.error(f"[{i}] parent_category_id => {parent_category_id}")
        pass

    def test_update_category_101(self):
        """
        異常系:
        次のように「親カテゴリ」が自身の子カテゴリを参照している場合に、
        ClientError(400)、かつ、所定のメッセージが表示されることを確認する。

          +-- 親カテゴリ <- 子カテゴリ1 <- 子カテゴリ2 <- 子カテゴリ3
          |                      ↑
          +----------------------+
        """
        company = Company.objects.first()
        c0 = Category.objects.create(company=company, name="C0")
        c1 = Category.objects.create(company=company, name="C1", parent_category=c0)
        c2 = Category.objects.create(company=company, name="C2", parent_category=c1)
        c3 = Category.objects.create(company=company, name="C3", parent_category=c2)

        payload = {"parent_category": str(c1.id)}
        response = self.client.patch(f"{self.TARGET_URL}{c0.id}/", payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("親カテゴリに子孫を指定できません", str(response.data))

    def test_update_category_102(self):
        """
        異常系:
        次のように「親カテゴリ」が自身の子カテゴリを参照している場合に、
        ClientError(400)、かつ、所定のメッセージが表示されることを確認する。

          +-- 親カテゴリ <- 子カテゴリ1 <- 子カテゴリ2 <- 子カテゴリ3
          |                                     ↑
          +-------------------------------------+
        """
        company = Company.objects.first()
        c0 = Category.objects.create(company=company, name="C0")
        c1 = Category.objects.create(company=company, name="C1", parent_category=c0)
        c2 = Category.objects.create(company=company, name="C2", parent_category=c1)
        c3 = Category.objects.create(company=company, name="C3", parent_category=c2)

        payload = {"parent_category": str(c2.id)}
        response = self.client.patch(f"{self.TARGET_URL}{c0.id}/", payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("親カテゴリに子孫を指定できません", str(response.data))

    def test_update_category_103(self):
        """
        異常系:
        次のように「親カテゴリ」が自身の子カテゴリを参照している場合に、
        ClientError(400)、かつ、所定のメッセージが表示されることを確認する。

          +-- 親カテゴリ <- 子カテゴリ1 <- 子カテゴリ2 <- 子カテゴリ3
          |                                                    ↑
          +----------------------------------------------------+
        """
        company = Company.objects.first()
        c0 = Category.objects.create(company=company, name="C0")
        c1 = Category.objects.create(company=company, name="C1", parent_category=c0)
        c2 = Category.objects.create(company=company, name="C2", parent_category=c1)
        c3 = Category.objects.create(company=company, name="C3", parent_category=c2)

        payload = {"parent_category": str(c3.id)}
        response = self.client.patch(f"{self.TARGET_URL}{c0.id}/", payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("親カテゴリに子孫を指定できません", str(response.data))

    def test_update_category_104(self):
        """
        異常系:
        次のように「親カテゴリ」が自身の子カテゴリを参照している場合に、
        ClientError(400)、かつ、所定のメッセージが表示されることを確認する。

              親カテゴリ <- 子カテゴリ1 <- 子カテゴリ2 <- 子カテゴリ3
                                 |              ↑
                                 +--------------+
        """
        company = Company.objects.first()
        c0 = Category.objects.create(company=company, name="C0")
        c1 = Category.objects.create(company=company, name="C1", parent_category=c0)
        c2 = Category.objects.create(company=company, name="C2", parent_category=c1)
        c3 = Category.objects.create(company=company, name="C3", parent_category=c2)

        payload = {"parent_category": str(c2.id)}
        response = self.client.patch(f"{self.TARGET_URL}{c1.id}/", payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("親カテゴリに子孫を指定できません", str(response.data))

    def test_update_category_105(self):
        """
        異常系:
        次のように「親カテゴリ」が自身の子カテゴリを参照している場合に、
        ClientError(400)、かつ、所定のメッセージが表示されることを確認する。

              親カテゴリ <- 子カテゴリ1 <- 子カテゴリ2 <- 子カテゴリ3
                                 |                             ↑
                                 +-----------------------------+
        """
        company = Company.objects.first()
        c0 = Category.objects.create(company=company, name="C0")
        c1 = Category.objects.create(company=company, name="C1", parent_category=c0)
        c2 = Category.objects.create(company=company, name="C2", parent_category=c1)
        c3 = Category.objects.create(company=company, name="C3", parent_category=c2)

        payload = {"parent_category": str(c3.id)}
        response = self.client.patch(f"{self.TARGET_URL}{c1.id}/", payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("親カテゴリに子孫を指定できません", str(response.data))

    def test_update_category_106(self):
        """
        異常系:
        次のように「親カテゴリ」が自身の子カテゴリを参照している場合に、
        ClientError(400)、かつ、所定のメッセージが表示されることを確認する。

              親カテゴリ <- 子カテゴリ1 <- 子カテゴリ2 <- 子カテゴリ3
                                                |              ↑
                                                +--------------+
        """
        company = Company.objects.first()
        c0 = Category.objects.create(company=company, name="C0")
        c1 = Category.objects.create(company=company, name="C1", parent_category=c0)
        c2 = Category.objects.create(company=company, name="C2", parent_category=c1)
        c3 = Category.objects.create(company=company, name="C3", parent_category=c2)

        payload = {"parent_category": str(c3.id)}
        response = self.client.patch(f"{self.TARGET_URL}{c2.id}/", payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("親カテゴリに子孫を指定できません", str(response.data))

    def test_update_category_107(self):
        """
        異常系:
        次のように「親カテゴリ」が自身の子カテゴリを参照している場合に、
        ClientError(400)、かつ、所定のメッセージが表示されることを確認する。

              親カテゴリ <- 子カテゴリ1 <- 子カテゴリ2 <- 子カテゴリ3
                                 |                             ↑
                                 +-----------------------------+
        """
        company = Company.objects.first()
        c0 = Category.objects.create(company=company, name="C0")
        c1 = Category.objects.create(company=company, name="C1", parent_category=c0)
        c2 = Category.objects.create(company=company, name="C2", parent_category=c1)
        c3 = Category.objects.create(company=company, name="C3", parent_category=c2)

        payload = {"parent_category": str(c3.id)}
        response = self.client.patch(f"{self.TARGET_URL}{c1.id}/", payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("親カテゴリに子孫を指定できません", str(response.data))

    def test_update_category_108(self):
        """
        異常系:
        次のように「対象のカテゴリ」が自分自身を参照している場合に、
        ClientError(400)、かつ、所定のメッセージが表示されることを確認する。

          +-- 親カテゴリ <- 子カテゴリ1 <- 子カテゴリ2 <- 子カテゴリ3
          |       ↑
          +-------+
        """
        company = Company.objects.first()
        c0 = Category.objects.create(company=company, name="C0")
        c1 = Category.objects.create(company=company, name="C1", parent_category=c0)
        c2 = Category.objects.create(company=company, name="C2", parent_category=c1)
        c3 = Category.objects.create(company=company, name="C3", parent_category=c2)

        payload = {"parent_category": str(c0.id)}
        response = self.client.patch(f"{self.TARGET_URL}{c0.id}/", payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("更新対象自身を親カテゴリに設定できません", str(response.data))

    def test_update_category_109(self):
        """
        異常系:
        次のように「対象のカテゴリ」が自分自身を参照している場合に、
        ClientError(400)、かつ、所定のメッセージが表示されることを確認する。

              親カテゴリ <- 子カテゴリ1 <- 子カテゴリ2 <- 子カテゴリ3
                             |       ↑
                             +-------+
        """
        company = Company.objects.first()
        c0 = Category.objects.create(company=company, name="C0")
        c1 = Category.objects.create(company=company, name="C1", parent_category=c0)
        c2 = Category.objects.create(company=company, name="C2", parent_category=c1)
        c3 = Category.objects.create(company=company, name="C3", parent_category=c2)

        payload = {"parent_category": str(c1.id)}
        response = self.client.patch(f"{self.TARGET_URL}{c1.id}/", payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("更新対象自身を親カテゴリに設定できません", str(response.data))

    def test_update_category_110(self):
        """
        異常系:
        次のように「対象のカテゴリ」が自分自身を参照している場合に、
        ClientError(400)、かつ、所定のメッセージが表示されることを確認する。

              親カテゴリ <- 子カテゴリ1 <- 子カテゴリ2 <- 子カテゴリ3
                                                           |       ↑
                                                           +-------+
        """
        company = Company.objects.first()
        c0 = Category.objects.create(company=company, name="C0")
        c1 = Category.objects.create(company=company, name="C1", parent_category=c0)
        c2 = Category.objects.create(company=company, name="C2", parent_category=c1)
        c3 = Category.objects.create(company=company, name="C3", parent_category=c2)

        payload = {"parent_category": str(c3.id)}
        response = self.client.patch(f"{self.TARGET_URL}{c3.id}/", payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("更新対象自身を親カテゴリに設定できません", str(response.data))

    def test_destroy_category_001(self):
        """
        正常系:
        次のように「子カテゴリ」を持たないカテゴリは削除できること。

              親カテゴリ <- 子カテゴリ1 <- 子カテゴリ2 <- 子カテゴリ3
                                                           |       ↑
                                                           +-------+
        """
        company = Company.objects.first()
        c0 = Category.objects.create(company=company, name="C0")
        c1 = Category.objects.create(company=company, name="C1", parent_category=c0)
        c2 = Category.objects.create(company=company, name="C2", parent_category=c1)
        c3 = Category.objects.create(company=company, name="C3", parent_category=c2)

        response = self.client.delete(f"{self.TARGET_URL}{c3.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Category.objects.filter(id=c3.id).exists())

    def test_destroy_category_101(self):
        """
        異常系:
        次のように「子カテゴリ」を持つカテゴリは削除できないこと。
        また、削除を試みた場合に、ClientError(400)、かつ、所定のメッセージが表示されること。

              親カテゴリ <- 子カテゴリ1 <- 子カテゴリ2 <- 子カテゴリ3
              |       ↑
              +-------+
        """
        company = Company.objects.first()
        c0 = Category.objects.create(company=company, name="C0")
        c1 = Category.objects.create(company=company, name="C1", parent_category=c0)
        c2 = Category.objects.create(company=company, name="C2", parent_category=c1)
        c3 = Category.objects.create(company=company, name="C3", parent_category=c2)

        response = self.client.delete(f"{self.TARGET_URL}{c0.id}/")
        self.assertEqual(response.status_code, 400)
        self.assertIn("子カテゴリを持つカテゴリは削除できません", str(response.data))
        self.assertTrue(Category.objects.filter(id=c0.id).exists())

    def test_destroy_category_102(self):
        """
        異常系:
        次のように「子カテゴリ」を持つカテゴリは削除できないこと。
        また、削除を試みた場合に、ClientError(400)、かつ、所定のメッセージが表示されること。

              親カテゴリ <- 子カテゴリ1 <- 子カテゴリ2 <- 子カテゴリ3
                             |       ↑
                             +-------+
        """
        company = Company.objects.first()
        c0 = Category.objects.create(company=company, name="C0")
        c1 = Category.objects.create(company=company, name="C1", parent_category=c0)
        c2 = Category.objects.create(company=company, name="C2", parent_category=c1)
        c3 = Category.objects.create(company=company, name="C3", parent_category=c2)

        response = self.client.delete(f"{self.TARGET_URL}{c1.id}/")
        self.assertEqual(response.status_code, 400)
        self.assertIn("子カテゴリを持つカテゴリは削除できません", str(response.data))
        self.assertTrue(Category.objects.filter(id=c1.id).exists())

    def test_destroy_category_103(self):
        """
        異常系:
        次のように「子カテゴリ」を持つカテゴリは削除できないこと。
        また、削除を試みた場合に、ClientError(400)、かつ、所定のメッセージが表示されること。

              親カテゴリ <- 子カテゴリ1 <- 子カテゴリ2 <- 子カテゴリ3
                                            |       ↑
                                            +-------+
        """
        company = Company.objects.first()
        c0 = Category.objects.create(company=company, name="C0")
        c1 = Category.objects.create(company=company, name="C1", parent_category=c0)
        c2 = Category.objects.create(company=company, name="C2", parent_category=c1)
        c3 = Category.objects.create(company=company, name="C3", parent_category=c2)

        response = self.client.delete(f"{self.TARGET_URL}{c1.id}/")
        self.assertEqual(response.status_code, 400)
        self.assertIn("子カテゴリを持つカテゴリは削除できません", str(response.data))
        self.assertTrue(Category.objects.filter(id=c1.id).exists())

    def test_destroy_category_104(self):
        """
        異常系:
        次のように「子カテゴリ」を持つカテゴリは削除できないこと。
        また、削除を試みた場合に、ClientError(400)、かつ、所定のメッセージが表示されること。

              親カテゴリ <- 子カテゴリ1 <- 子カテゴリ2 <- 子カテゴリ3
                                                           |       ↑
                                                           +-------+
        """
        company = Company.objects.first()
        c0 = Category.objects.create(company=company, name="C0")
        c1 = Category.objects.create(company=company, name="C1", parent_category=c0)
        c2 = Category.objects.create(company=company, name="C2", parent_category=c1)
        c3 = Category.objects.create(company=company, name="C3", parent_category=c2)

        response = self.client.delete(f"{self.TARGET_URL}{c1.id}/")
        self.assertEqual(response.status_code, 400)
        self.assertIn("子カテゴリを持つカテゴリは削除できません", str(response.data))
        self.assertTrue(Category.objects.filter(id=c1.id).exists())

