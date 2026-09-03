from types import SimpleNamespace

from django.test import TestCase
from rest_framework.exceptions import ValidationError

from api.models import Category, Company
from api.validators import NoCircularParentCategoryValidator, SameCompanyParentCategoryValidator


def serializer_for(instance=None):
    # バリデータは serializer.instance しか参照しないため、Serializer 本体を組み立てずに済ませる
    return SimpleNamespace(instance=instance)


class SameCompanyParentCategoryValidatorTests(TestCase):
    def setUp(self):
        self.validator = SameCompanyParentCategoryValidator()
        self.company = Company.objects.create(name="テスト企業")
        self.other_company = Company.objects.create(name="別企業")
        self.parent = Category.objects.create(company=self.company, name="食品")
        self.other_parent = Category.objects.create(company=self.other_company, name="食品")

    def test_passes_without_parent(self):
        self.validator({"company": self.company, "name": "菓子"}, serializer_for())

    def test_passes_when_parent_belongs_to_same_company(self):
        self.validator({"company": self.company, "parent_category": self.parent}, serializer_for())

    def test_rejects_parent_of_other_company(self):
        with self.assertRaises(ValidationError) as ctx:
            self.validator({"company": self.company, "parent_category": self.other_parent}, serializer_for())

        self.assertIn("parent_category", ctx.exception.detail)

    def test_falls_back_to_instance_company_on_partial_update(self):
        child = Category.objects.create(company=self.company, name="菓子")

        # PATCH で parent_category だけを送った場合、company はインスタンスの値で判定される
        self.validator({"parent_category": self.parent}, serializer_for(child))
        with self.assertRaises(ValidationError):
            self.validator({"parent_category": self.other_parent}, serializer_for(child))

    def test_falls_back_to_instance_parent_on_partial_update(self):
        child = Category.objects.create(company=self.company, name="菓子", parent_category=self.parent)

        # PATCH で company だけを別企業に変えると、既存の親が別企業になるため拒否される
        with self.assertRaises(ValidationError):
            self.validator({"company": self.other_company}, serializer_for(child))


class NoCircularParentCategoryValidatorTests(TestCase):
    def setUp(self):
        self.validator = NoCircularParentCategoryValidator()
        company = Company.objects.create(name="テスト企業")
        self.root = Category.objects.create(company=company, name="食品")
        self.child = Category.objects.create(company=company, name="菓子", parent_category=self.root)
        self.grandchild = Category.objects.create(company=company, name="チョコレート", parent_category=self.child)
        self.sibling = Category.objects.create(company=company, name="飲料")

    def test_skips_on_create(self):
        # 新規作成時はまだ子孫を持たないため循環は成立しない
        self.validator({"parent_category": self.root}, serializer_for())

    def test_passes_without_parent(self):
        self.validator({"parent_category": None}, serializer_for(self.root))

    def test_passes_when_parent_is_unrelated(self):
        self.validator({"parent_category": self.sibling}, serializer_for(self.root))

    def test_passes_when_parent_is_ancestor(self):
        self.validator({"parent_category": self.root}, serializer_for(self.grandchild))

    def test_rejects_self_as_parent(self):
        with self.assertRaises(ValidationError) as ctx:
            self.validator({"parent_category": self.root}, serializer_for(self.root))

        self.assertIn("parent_category", ctx.exception.detail)

    def test_rejects_child_as_parent(self):
        with self.assertRaises(ValidationError):
            self.validator({"parent_category": self.child}, serializer_for(self.root))

    def test_rejects_grandchild_as_parent(self):
        with self.assertRaises(ValidationError):
            self.validator({"parent_category": self.grandchild}, serializer_for(self.root))

    def test_falls_back_to_instance_parent_on_partial_update(self):
        # parent_category を送らない PATCH では既存の親で判定され、既存データに循環は無いので通る
        self.validator({"name": "お菓子"}, serializer_for(self.child))
