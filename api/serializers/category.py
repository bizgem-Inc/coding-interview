from rest_framework.serializers import ModelSerializer

from ..models.category import Category


class CategoryModelSerializer(ModelSerializer):
    class Meta:
        model = Category
        exclude = ("company",)