from rest_framework import serializers


class CategoryRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    parent_category_id = serializers.UUIDField(required=False, allow_null=True)


class CategoryResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(max_length=255, read_only=True)
    parent_category_id = serializers.UUIDField(allow_null=True, read_only=True)


# Get


class CategoryGetAPIResponseSerializer(CategoryResponseSerializer):
    pass


class CategoryListAPIResponseSerializer(CategoryResponseSerializer):
    pass


# Post


class CategoryPostAPIRequestSerializer(CategoryRequestSerializer):
    company_id = serializers.UUIDField()


class CategoryPostAPIResponseSerializer(CategoryResponseSerializer):
    pass


# Patch


class CategoryPatchAPIRequestSerializer(CategoryRequestSerializer):
    pass
