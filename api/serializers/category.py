from typing import Any

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.models import Category, Company


class CategorySerializer(serializers.ModelSerializer):
    """カテゴリの入出力とバリデーションを行う。

    company と parent_category は ID(UUID)で受け取り、ID で返す。

    バリデーション:
        - name は前後の空白を除いたうえで、空文字を禁止し、255 文字以内とする
        - 同一企業内で name の重複を禁止する
        - parent_category は同じ企業のカテゴリに限る
        - 自分自身や子孫を parent_category にする循環を禁止する
        - 作成後の company の変更を禁止する
    """

    class Meta:
        model = Category
        fields = ["id", "company", "name", "parent_category", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
        # DRF 3.14 は Meta.constraints の UniqueConstraint からバリデータを生成しないため明示する
        validators = [
            UniqueTogetherValidator(
                queryset=Category.objects.all(),
                fields=["company", "name"],
                message="Category with this name already exists in the company.",
            )
        ]

    def validate_company(self, value: Company) -> Company:
        """更新時に company が変更されていないことを検証する。

        企業をまたいで移動すると親子関係の整合を取り直す必要があるため、作成後の変更を禁止する。
        """
        if self.instance is not None and value.pk != self.instance.company_id:
            raise serializers.ValidationError("Company cannot be changed.")
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """parent_category が同じ企業のカテゴリで、循環を作らないことを検証する。"""
        parent = attrs.get("parent_category")
        if parent is None:
            return attrs

        # PATCH で company が省略された場合は、更新対象の企業と比較する
        company_id = attrs["company"].pk if "company" in attrs else self.instance.company_id
        if parent.company_id != company_id:
            raise serializers.ValidationError({"parent_category": "Parent category must belong to the same company."})

        # 作成時は子を持たないため、循環が起こり得るのは更新時だけ
        if self.instance is not None and self._is_self_or_descendant(parent):
            raise serializers.ValidationError({"parent_category": "Category cannot be its own parent or descendant."})

        return attrs

    def _is_self_or_descendant(self, category: Category | None) -> bool:
        """category が更新対象のカテゴリ自身か、その子孫であれば True を返す。

        category から祖先方向にたどり、更新対象に到達するかで判定する。
        1 階層ごとに 1 クエリが発生する。既存データが循環していても止まるよう、訪問済みの ID を記録する。
        """
        visited = set()
        while category is not None and category.pk not in visited:
            if category.pk == self.instance.pk:
                return True
            visited.add(category.pk)
            category = category.parent_category
        return False
