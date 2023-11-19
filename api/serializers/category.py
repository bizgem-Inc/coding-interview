from rest_framework import serializers

from ..models import (
    category,
    company as mode_company
)


class ListSerializer(serializers.ModelSerializer):

    class Meta:
        model = category.Category
        fields = ("id",
                  "name",
                  "parent_category_id",
                  "company_id",
                  "created_at",
                  "updated_at")
    parent_category_id = serializers.PrimaryKeyRelatedField(
        label="親カテゴリID",
        queryset=category.Category.objects.all(),
        required=False)


class RetrieveSerializer(serializers.ModelSerializer):

    class CompanySerializer(serializers.ModelSerializer):
        class Meta:
            model = mode_company.Company
            fields = "__all__"

    class ParentCategorySerializer(serializers.ModelSerializer):
        class Meta:
            model = category.Category
            fields = ("id",
                      "name",
                      "created_at",
                      "updated_at")

    class Meta:
        model = category.Category
        fields = ("id",
                  "name",
                  "company",
                  "parent_category",
                  "created_at",
                  "updated_at")
    company = CompanySerializer(read_only=True)
    parent_category = ParentCategorySerializer(read_only=True)


class CreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = category.Category
        fields = ("id",
                  "name",
                  "company_id",
                  "parent_category_id")
        read_only_fields = ("id",)

    company_id = serializers.PrimaryKeyRelatedField(
        label="企業ID",
        queryset=mode_company.Company.objects.all(),
        required=True)

    parent_category_id = serializers.PrimaryKeyRelatedField(
        label="親カテゴリID",
        queryset=category.Category.objects.all(),
        required=False)

    def create(self, validated_data):
        # objectとして渡されるため、保存用にidに変換
        validated_data["company_id"] = validated_data["company_id"].id

        # 必須の値ではないため、存在確認しつつ置き換えて更新
        if "parent_category_id" in validated_data:
            validated_data["parent_category_id"] = \
                validated_data["parent_category_id"].id
        return super().create(validated_data)


class UpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = category.Category
        fields = ("id",
                  "name",
                  "company_id",
                  "parent_category_id")
        read_only_fields = ("id",)

    # 更新時は必須項目としない
    company_id = serializers.PrimaryKeyRelatedField(
        label="企業ID",
        queryset=mode_company.Company.objects.all(),
        required=False)

    parent_category_id = serializers.PrimaryKeyRelatedField(
        label="親カテゴリID",
        queryset=category.Category.objects.all(),
        required=False)

    def update(self, instance, validated_data):
        # 必須の値ではないため、存在確認しつつ置き換えて更新
        if "company_id" in validated_data:
            validated_data["company_id"] = validated_data["company_id"].id

        if "parent_category_id" in validated_data:
            validated_data["parent_category_id"] = \
                validated_data["parent_category_id"].id

        return super().update(instance, validated_data)


class DestroySerializer(serializers.ModelSerializer):

    class Meta:
        model = category.Category
        fields = ("id",)
