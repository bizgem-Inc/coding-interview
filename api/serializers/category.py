from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.models.category import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "company", "name", "parent_category"]
        validators = [
            UniqueTogetherValidator(
                queryset=Category.objects.all(),
                fields=["company", "name"],
            )
        ]

    def validate(self, attrs):
        # 部分更新でリクエストに含まれないフィールドは既存の値で検証する
        if "parent_category" in attrs:
            parent = attrs["parent_category"]
        elif self.instance is not None:
            parent = self.instance.parent_category
        else:
            parent = None

        if parent is None:
            return attrs

        company = attrs.get("company") or (self.instance.company if self.instance else None)

        if company is not None and parent.company_id != company.id:
            raise serializers.ValidationError(
                {"parent_category": "別の企業のカテゴリを親カテゴリに指定することはできません。"}
            )
        if self.instance is not None and parent.pk == self.instance.pk:
            raise serializers.ValidationError(
                {"parent_category": "自分自身を親カテゴリに指定することはできません。"}
            )
        return attrs
