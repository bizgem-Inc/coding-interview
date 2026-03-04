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
                message="同じ企業内でカテゴリ名が重複しています。",
            )
        ]

    def validate_name(self, value):
        """カテゴリ名のバリデーション"""
        if not value or not value.strip():
            raise serializers.ValidationError("カテゴリ名は空にできません。")
        return value.strip()

    def validate(self, data):
        """オブジェクトレベルのバリデーション"""
        parent_category = data.get("parent_category")

        # 部分更新の場合、リクエストに含まれないフィールドは既存のインスタンスから取得
        company = data.get("company")
        if company is None and self.instance:
            company = self.instance.company

        if parent_category is not None:
            # 親カテゴリが同じ企業に属しているか検証
            if company and parent_category.company_id != company.id:
                raise serializers.ValidationError(
                    {"parent_category": "親カテゴリは同じ企業に属している必要があります。"}
                )

            # 循環参照の検証（更新時のみ関連）
            if self.instance:
                current = parent_category
                while current is not None:
                    if current.id == self.instance.id:
                        raise serializers.ValidationError(
                            {"parent_category": "循環参照が発生するため、この親カテゴリは設定できません。"}
                        )
                    current = current.parent_category

        return data

