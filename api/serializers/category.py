from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField

from ..models.category import Category


class CategoryModelSerializer(ModelSerializer):
    parent_category = PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Category
        exclude = ("company",)