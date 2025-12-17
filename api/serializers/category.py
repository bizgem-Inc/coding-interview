from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from api.models.category import Category
import logging

logger = logging.getLogger(__name__)

# カテゴリの深度の最大値。(際限無く深度が大きくなることを避けるための独自仕様)
MAX_DEPTH = 6


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        validators = [
            UniqueTogetherValidator(
                # 重複する company と name のペアを持つことは不可であることを明示する
                queryset=Category.objects.all(),
                fields=("company", "name"),
                message="すでに、指定の「企業ID」と「カテゴリ名」のペアが存在しています。",
            ),
        ]

    def validate(self, attrs):
        parent_category = attrs.get("parent_category")
        # 更新対象自身 (/api/categories/<uuid:pk>) と 親カテゴリ (parent_category) が同一か否かを検査する
        if self.instance is not None and parent_category is not None:
            if self.instance.id == parent_category.id:
                raise serializers.ValidationError(
                    "更新対象自身を親カテゴリに設定できません"
                )
        """
        次のように「親カテゴリ」が自身の子カテゴリを参照していないかを検査する

          +-- 親カテゴリ <- 子カテゴリ1 <- 子カテゴリ2 <- 子カテゴリ3
          |                                     ↑
          +-------------------------------------+
        """
        if (self.instance is not None) and (parent_category is not None):
            cur = parent_category
            # 祖先を根までたどる
            while cur is not None:
                if cur.id == self.instance.id:
                    raise serializers.ValidationError(
                        "親カテゴリに子孫を指定できません"
                    )
                cur = cur.parent_category

        """
        カテゴリの親子関係の深さ検査
        新規作成時は self.instance が None なので parent から数え上げる
        """
        depth = 1
        cur = parent_category
        while cur is not None:
            depth += 1
            if depth > MAX_DEPTH:
                raise serializers.ValidationError(
                    f"カテゴリ階層は最大{MAX_DEPTH}階層までにしてください"
                )
            cur = cur.parent_category
        return attrs
