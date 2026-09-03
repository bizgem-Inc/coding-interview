from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.models import Category
from api.validators import NoCircularParentCategoryValidator, SameCompanyParentCategoryValidator


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "company", "name", "parent_category", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
        validators = [
            # DRF 3.14 は Meta.constraints の UniqueConstraint を自動検出しないため明示する
            UniqueTogetherValidator(
                queryset=Category.objects.all(),
                fields=["company", "name"],
                message="同じ企業内に同名のカテゴリが既に存在します。",
            ),
            SameCompanyParentCategoryValidator(),
            NoCircularParentCategoryValidator(),
        ]
