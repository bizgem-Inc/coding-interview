# api/serializers/category.py
from rest_framework import serializers

from api.models import Category


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

    def validate(self, attrs):
        """
        parent_category を指定する場合、同じ company の Category であることをチェック
        """
        company = attrs.get("company") or getattr(self.instance, "company", None)
        parent = attrs.get("parent_category") or getattr(
            self.instance, "parent_category", None
        )

        if parent and company and parent.company_id != company.id:
            raise serializers.ValidationError(
                "parent_category は同じ company のカテゴリを指定してください。"
            )

        return attrs
