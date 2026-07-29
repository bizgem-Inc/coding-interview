from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from ..models import Category


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
                message="同じ企業に同名のカテゴリがすでに存在します",
            )
        ]

    def validate(self, attrs):
        company = attrs.get(
            "company",
            self.instance.company if self.instance else None,
        )
        parent_category = attrs.get(
            "parent_category",
            self.instance.parent_category if self.instance else None,
        )

        if parent_category is None:
            return attrs

        if self.instance and parent_category.pk == self.instance.pk:
            raise serializers.ValidationError(
                {
                    "parent_category": "自分自身を親カテゴリに指定することはできません。"
                }
            )

        if parent_category.company_id != company.pk:
            raise serializers.ValidationError(
                {
                    "parent_category": (
                        "親カテゴリは同じ企業に属するカテゴリである必要があります。"
                    )
                }
            )

        return attrs
