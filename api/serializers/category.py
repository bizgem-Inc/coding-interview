from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.models.category import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "company",
            "name",
            "parent_category",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
        validators = [
            UniqueTogetherValidator(
                queryset=Category.objects.all(),
                fields=("company", "name"),
                message="同一企業内でカテゴリ名が重複しています。",
            )
        ]

    def validate_parent_category(self, parent: Category | None) -> Category | None:
        if parent is None:
            return parent
        company_id: str | None = self.initial_data.get("company") or (
            self.instance.company_id if self.instance else None
        )
        if str(parent.company_id) != str(company_id):
            raise serializers.ValidationError(
                "parent_category は同じ company に属している必要があります。"
            )
        if self.instance and parent.pk == self.instance.pk:
            raise serializers.ValidationError(
                "自身を parent_category に指定することはできません。"
            )
        ancestor: Category | None = parent.parent_category
        while ancestor is not None:
            if self.instance and ancestor.pk == self.instance.pk:
                raise serializers.ValidationError("循環参照になります。")
            ancestor = ancestor.parent_category
        return parent
