from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.models import Category


class CategorySerializer(serializers.ModelSerializer):
    """Category モデル用のシリアライザ"""

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
            )
        ]
