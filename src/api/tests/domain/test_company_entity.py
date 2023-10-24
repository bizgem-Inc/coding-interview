from django.test import TestCase
from uuid import uuid4
from datetime import datetime
from domain.entity.company import CompanyEntity

class CompanyEntityTestCase(TestCase):

    def test_new_entity(self):
        """
        初めてエンティティが生成される際にアプリケーション側ではidやcreated_at, updated_atを設定しない
        入れた値については正しいことを確認
        """
        company = CompanyEntity.new("Test Company")
        self.assertIsNone(company.id)
        self.assertIsNone(company.created_at)
        self.assertIsNone(company.updated_at)

        self.assertEqual(company.name, "Test Company")

    def test_from_record(self):
        """
        永続化された既存データからエンティティを生成する際にはidやcreated_at, updated_atを設定される
        入れた値は正しいことを確認
        """
        company = CompanyEntity.from_record(
            uuid4(), "Test Company", datetime.now(), datetime.now()
        )
        self.assertIsNotNone(company.id)
        self.assertIsNotNone(company.created_at)
        self.assertIsNotNone(company.updated_at)

        self.assertEqual(company.name, "Test Company")

    def test_validate_name(self):
        """
        名前のバリデーションのしきい値テスト、not validパターン
        """
        with self.assertRaises(ValueError):
            CompanyEntity.new("a" * 256)

    def test_validate_name_ok(self):
        """
        名前のバリデーションのしきい値テスト、validパターン
        """
        company = CompanyEntity.new("a" * 255)
        self.assertEqual(company.name, "a" * 255)

    def test_to_dict(self):
        """
        to_dictメソッドが正しく動作するか確認
        """
        company = CompanyEntity.from_record(
            uuid4(), "Test Company", datetime.now(), datetime.now()
        )
        result = company.to_dict()

        self.assertEqual(result["id"], str(company.id))
        self.assertEqual(result["name"], company.name)
        self.assertEqual(result["created_at"], company.created_at.isoformat())
        self.assertEqual(result["updated_at"], company.updated_at.isoformat())
