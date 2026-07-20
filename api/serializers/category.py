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
                message="同じ企業内に同名のカテゴリが既に存在します。",
            )
        ]

    def validate(self, attrs):
        company = attrs.get("company", getattr(self.instance, "company", None))
        parent_category = attrs.get("parent_category", getattr(self.instance, "parent_category", None))

        if parent_category:
            # 自身をparentにしたときの循環を防ぐ
            if self.instance and parent_category.id == self.instance.id:
                raise serializers.ValidationError({"parent_category": "自分自身を親カテゴリに指定することはできません。"})
            
            # 他社のカテゴリを親に持たないようにする
            if parent_category.company_id != company.id:
                raise serializers.ValidationError({"parent_category": "異なる企業のカテゴリを親カテゴリに指定することはできません。"})

        return attrs
