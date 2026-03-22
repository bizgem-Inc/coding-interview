from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.models.category import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "company",
            "name",
            "parent_category",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
        # ユニーク制約: companyとnameの組み合わせはユニークである必要がある
        validators = [
            UniqueTogetherValidator(
                queryset=Category.objects.all(),
                fields=("company", "name"),
                message="この会社には既に同名のカテゴリが存在します。",
            )
        ]

    def validate(self, data):
        company = data.get("company")
        parent_category = data.get("parent_category")

        if self.instance:
            if "company" not in data:
                company = self.instance.company
            if "parent_category" not in data:
                parent_category = self.instance.parent_category

        if parent_category:
            # 1. 自分自身を親カテゴリに設定できないこと（更新時）
            if self.instance and parent_category.id == self.instance.id:
                raise serializers.ValidationError({"parent_category": "自分自身を親カテゴリに設定することはできません。"})

            # 2. 親カテゴリは同じ会社であること
            if company and parent_category.company_id != company.id:
                raise serializers.ValidationError({"parent_category": "親カテゴリは同じ会社のものを指定してください。"})

        return data
