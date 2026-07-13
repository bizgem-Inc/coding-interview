from django.conf import settings
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.models.category import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "company",
            "name",
            "parent_category",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

        validators = [
            UniqueTogetherValidator(
                queryset=Category.objects.all(),
                fields=["company", "name"],
                message="Category with this name already exists in this company.",
            )
        ]

    def validate_company(self, value):
        # NOTE: read_only_fieldsにcompanyを含めると、UniqueTogetheValidatorが正しく機能しないため個別にバリデーションを行う
        if not self.instance:
            return value

        # 作成済みカテゴリの所属企業の変更チェック
        if self.instance.company_id != value.id:
            raise serializers.ValidationError("Company cannot be changed.")

        return value

    def validate_parent_category(self, value):
        if not value:
            return value

        if self.instance and value.id == self.instance.id:
            raise serializers.ValidationError("Cannot set itself as a parent category.")

        ancestor = value
        checked_ids = set()

        while ancestor is not None:
            if self.instance and ancestor.id == self.instance.id:
                # 子孫を親にした場合のエラー
                raise serializers.ValidationError("Cannot set its descendant as a parent category.")

            if ancestor.id in checked_ids:
                # 既に親カテゴリで循環参照が発生している場合のエラー
                raise serializers.ValidationError("Circular reference detected.")

            checked_ids.add(ancestor.id)
            ancestor = ancestor.parent_category

        return value

    def validate(self, attrs):
        parent_category = attrs.get("parent_category", getattr(self.instance, "parent_category", None))
        company = attrs.get("company", getattr(self.instance, "company", None))

        # 親カテゴリーと所属企業の整合性チェック
        self._validate_parent_company_integrity(parent_category, company)

        return attrs

    def _validate_parent_company_integrity(self, parent_category, company):
        if not parent_category:
            return

        if parent_category.company_id != company.id:
            raise serializers.ValidationError(
                {"parent_category": "Parent category must belong to the same company."}
            )