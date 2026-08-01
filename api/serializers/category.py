from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.models.category import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "company", "name", "parent_category", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
        validators = [
            UniqueTogetherValidator(
                queryset=Category.objects.all(),
                fields=["company", "name"],
                message="このカテゴリ名は既に同じ企業内で使用されています。",
            )
        ]

    def validate(self, attrs):
        instance = self.instance

        if "company" in attrs:
            company = attrs["company"]
        else:
            company = instance.company if instance else None

        if "parent_category" in attrs:
            parent_category = attrs["parent_category"]
        else:
            parent_category = instance.parent_category if instance else None

        if parent_category is not None:
            if company is not None and parent_category.company_id != company.id:
                raise serializers.ValidationError({"parent_category": "親カテゴリは同じ企業のカテゴリを指定してください。"})

            if instance is not None:
                ancestor = parent_category
                while ancestor is not None:
                    if ancestor.id == instance.id:
                        raise serializers.ValidationError({"parent_category": "親カテゴリに自分自身または自分の子孫を指定することはできません。"})
                    ancestor = ancestor.parent_category

        return attrs
