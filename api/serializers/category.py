from rest_framework import serializers

from api.models.category import Category
from api.models.company import Company


class NestedCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "name"]


class NestedCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "company", "name", "parent_category", "created_at", "updated_at"]


class CategoryDetailSerializer(serializers.ModelSerializer):
    company = NestedCompanySerializer(read_only=True)
    parent_category = NestedCategorySerializer(read_only=True)

    class Meta:
        model = Category
        fields = ["id", "company", "name", "parent_category", "created_at", "updated_at"]


class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["company", "name", "parent_category"]

    def validate(self, data):
        parent_category = data.get("parent_category")
        if parent_category and parent_category.company != data["company"]:
            raise serializers.ValidationError(
                {"parent_category": "Parent category must belong to the same company."}
            )
        return data
