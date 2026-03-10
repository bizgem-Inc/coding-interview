from rest_framework import serializers

from api.models.category import Category


class CategorySerializer(serializers.ModelSerializer):
    parent_category_id = serializers.UUIDField(
        required=False,
        allow_null=True,
        write_only=False,
    )

    class Meta:
        model = Category
        fields = ["id", "company", "name", "parent_category_id", "created_at", "updated_at"]
        read_only_fields = ["id", "company", "created_at", "updated_at"]
