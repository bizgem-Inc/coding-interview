from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.models import Category


class CategorySerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        company = self.instance.company if self.instance else attrs.get("company")
        parent = attrs.get("parent_category")
        if parent is not None and parent.company_id != company.id:
            raise serializers.ValidationError(
                {"parent_category": "親カテゴリは同じ会社に属している必要があります。"}
            )
        return attrs

    def validate_company(self, value):
        if self.instance is not None and value != self.instance.company:
            raise serializers.ValidationError("company は作成後に変更できません。")
        return value

    def validate_parent_category(self, value):
        if value is None:
            return value
        if self.instance is None:
            return value
        ancestor = value
        while ancestor is not None:
            if ancestor.pk == self.instance.pk:
                raise serializers.ValidationError("循環する親子関係は指定できません。")
            ancestor = ancestor.parent_category
        return value

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
                message="同じ会社に同名のカテゴリが既に存在します。",
            )
        ]
