from rest_framework import serializers

from ..models.category import Category


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
        - parent_category は同じ company のカテゴリだけ許可
        - 自分自身を parent にするのはNG
        """
        instance = getattr(self, "instance", None)

        company = attrs.get("company") or (instance.company if instance else None)
        parent = attrs.get("parent_category") or (instance.parent_category if instance else None)

        if instance and parent and parent.id == instance.id:
            raise serializers.ValidationError({"parent_category": "parent_category cannot be itself."})

        if company and parent and parent.company_id != company.id:
            raise serializers.ValidationError({"parent_category": "parent_category must belong to the same company."})

        return attrs
