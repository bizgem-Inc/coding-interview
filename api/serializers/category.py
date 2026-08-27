from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "company", "name", "parent_category", "created_at", "updated_at"]
        # Category.Meta.constraints の UniqueConstraint は DRF が自動検知しない
        # (unique_together のみ対象) ため、400 を返せるよう明示的に宣言する
        validators = [
            UniqueTogetherValidator(queryset=Category.objects.all(), fields=["company", "name"]),
        ]

    def validate(self, attrs):
        parent_category = attrs.get("parent_category", getattr(self.instance, "parent_category", None))
        if parent_category is None:
            return attrs

        company = attrs.get("company", getattr(self.instance, "company", None))
        if parent_category.company_id != company.id:
            raise serializers.ValidationError(
                {"parent_category": "Parent category must belong to the same company."}
            )

        if self.instance is not None and self._is_self_or_descendant(parent_category):
            raise serializers.ValidationError(
                {"parent_category": "Parent category must not be itself or one of its descendants."}
            )

        return attrs

    def _is_self_or_descendant(self, parent_category):
        """parent_category が更新対象自身、またはその子孫かどうかを祖先を辿って判定する。"""
        # ponytail: 祖先を1件ずつ辿るため階層の深さだけクエリが出る。
        # 階層が深くなるようなら再帰CTEでの一括取得に置き換える。
        seen = set()
        node = parent_category
        while node is not None and node.pk not in seen:
            if node.pk == self.instance.pk:
                return True
            seen.add(node.pk)
            node = node.parent_category
        return False
