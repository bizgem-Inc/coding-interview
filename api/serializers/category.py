from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.models.category import Category


class CategorySerializer(serializers.ModelSerializer):
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
        # DRF 3.14 はモデルの UniqueConstraint からバリデータを自動生成しないため、
        # 同一企業内でのカテゴリ名の重複を 400 で返せるよう明示的に指定する
        validators = [
            UniqueTogetherValidator(
                queryset=Category.objects.all(),
                fields=["company", "name"],
            )
        ]
