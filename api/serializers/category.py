from __future__ import annotations

from typing import Any

from rest_framework import serializers

from api.models.category import Category


class CategorySerializer(serializers.ModelSerializer):
    # APIとして公開するCategoryのフィールドと、入力時の検証をまとめる。
    class Meta:
        model = Category
        fields = ["id", "company", "name", "parent_category", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

        # company/nameの重複はnameの入力エラーとして返したいので、標準の複合一意バリデータは使わない。
        validators = []
        extra_kwargs = {
            # 親を持たないルートカテゴリも作成できるようにする。
            "parent_category": {"allow_null": True, "required": False},
        }

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        instance = self.instance

        # PATCHなどで未指定の項目があっても、現在値を含めて整合性を確認する。
        company = attrs.get("company", instance.company if instance else None)
        name = attrs.get("name", instance.name if instance else None)
        parent_category = attrs.get(
            "parent_category",
            instance.parent_category if instance else None,
        )

        if parent_category and company and parent_category.company_id != company.id:
            # 企業をまたいだ親子関係はデータ構造として扱いづらいため拒否する。
            raise serializers.ValidationError(
                {"parent_category": "Parent category must belong to the same company."}
            )

        if instance and parent_category and parent_category.id == instance.id:
            # 自分自身を親にすると循環参照になるため拒否する。
            raise serializers.ValidationError(
                {"parent_category": "A category cannot be its own parent."}
            )

        if company and name:
            # モデル制約と同じ条件を事前に見て、DBエラーではなく400レスポンスとして返す。
            duplicate_categories = Category.objects.filter(company=company, name=name)
            if instance:
                # 更新時は自分自身のレコードを重複判定から外す。
                duplicate_categories = duplicate_categories.exclude(pk=instance.pk)

            if duplicate_categories.exists():
                raise serializers.ValidationError(
                    {"name": "Category with this name already exists for this company."}
                )

        return attrs
