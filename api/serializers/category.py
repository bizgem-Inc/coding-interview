from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from ..models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "company", "name", "parent_category", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
        # DRF は Meta.constraints を見ないため自動生成されない。明示的に付与しないと重複登録が 500 になる。
        validators = [
            UniqueTogetherValidator(
                queryset=Category.objects.all(),
                fields=["company", "name"],
                message="同一企業内に同名のカテゴリが既に存在します。",
            )
        ]

    def validate(self, attrs):
        parent_category = attrs.get("parent_category")
        if parent_category is None:
            return attrs

        company = attrs.get("company") or (self.instance.company if self.instance else None)
        if company is not None and parent_category.company_id != company.id:
            raise serializers.ValidationError({"parent_category": "親カテゴリは同一企業のカテゴリである必要があります。"})

        if self.instance is not None:
            if parent_category.id == self.instance.id:
                raise serializers.ValidationError({"parent_category": "自分自身を親カテゴリに設定することは出来ません。"})
            if self._causes_cycle(parent_category, self.instance.id):
                raise serializers.ValidationError({"parent_category": "親カテゴリの設定が循環しています。"})

        return attrs

    @staticmethod
    def _causes_cycle(parent_category, instance_id):
        """parent_category を親に設定した場合に instance_id を含む循環が発生するかを判定する。"""
        seen = set()
        current = parent_category
        while current is not None and current.id not in seen:
            if current.id == instance_id:
                return True
            seen.add(current.id)
            current = current.parent_category
        return False
