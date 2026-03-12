from typing import Any, Dict, Optional

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.models.category import Category


class CategorySerializer(serializers.ModelSerializer):
    """
    カテゴリ用のシリアライザ
    """

    class Meta:
        model = Category
        fields = "__all__"
        # メッセージをカスタマイズするため明示的に記述
        validators = [
            UniqueTogetherValidator(
                queryset=Category.objects.all(),
                fields=["company", "name"],
                message="同じ企業内に同じ名前のカテゴリが既に存在します。",
            )
        ]

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        instance: Optional[Category] = self.instance
        # PATCH対応：attrsにない場合は既存のインスタンスから取得
        company: Any = attrs.get("company", getattr(instance, "company", None))
        parent_category: Optional[Category] = attrs.get("parent_category", getattr(instance, "parent_category", None))

        # 親カテゴリの企業所属チェック
        if parent_category and company:
            # IDによる比較で効率化
            company_id: Any = company.id if hasattr(company, "id") else company
            if parent_category.company_id != company_id:
                raise serializers.ValidationError({"parent_category": "親カテゴリは同じ企業に属している必要があります。"})

        # 循環参照および階層の深さチェック
        if parent_category:
            if instance and parent_category.id == instance.id:
                raise serializers.ValidationError({"parent_category": "自分自身を親カテゴリに設定することはできません。"})

            # 再帰的に親を辿ってチェック
            curr: Optional[Category] = parent_category
            depth: int = 1  # parent_category 自体が1階層目
            MAX_DEPTH: int = 10  # 業務上の考慮に基づく最大深度

            while curr:
                if instance and curr.id == instance.id:
                    raise serializers.ValidationError({"parent_category": "循環参照が発生するため、このカテゴリを親に設定できません。"})

                curr = curr.parent_category
                depth += 1
                # 深さが業務上の合理的な範囲を超える場合はエラーとする
                if depth > MAX_DEPTH:
                    raise serializers.ValidationError({"parent_category": f"カテゴリの階層は最大{MAX_DEPTH}段階までです。"})

        return attrs