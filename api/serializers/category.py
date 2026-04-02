from typing import Any

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.models.category import Category


class CategorySerializer(serializers.ModelSerializer):
    """Serialize category data and enforce category validation rules."""

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
                message="A category with this company and name already exists.",
            )
        ]

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        company = attrs.get("company")
        parent_category = attrs.get("parent_category")

        if self.instance is not None:
            company = company or self.instance.company
            parent_category = attrs.get(
                "parent_category",
                self.instance.parent_category,
            )

        if (
            company is not None
            and parent_category is not None
            and parent_category.company_id != company.id
        ):
            raise serializers.ValidationError(
                {
                    "parent_category": [
                        "Parent category must belong to the same company.",
                    ]
                }
            )

        return attrs
