from rest_framework import serializers

from api.models.category import Category
from api.models.company import Company


# --- Nested Serializers ---


class NestedCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "name"]


class NestedCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


# --- Response Serializers ---


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


# --- Request Serializers ---


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


class CategoryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["name", "parent_category"]

    def validate(self, data):
        parent_category = data.get("parent_category")
        if parent_category:
            if parent_category.id == self.instance.id:
                raise serializers.ValidationError(
                    {"parent_category": "Cannot set self as parent category."}
                )
            if parent_category.company != self.instance.company:
                raise serializers.ValidationError(
                    {"parent_category": "Parent category must belong to the same company."}
                )

        name = data.get("name")
        if name and Category.objects.filter(
            company=self.instance.company, name=name
        ).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError(
                {"name": "Category with this name already exists in this company."}
            )

        return data
