from typing import Any, Optional

from rest_framework import serializers

from api.models.category import Category
from api.models.company import Company


class CategorySerializer(serializers.ModelSerializer):
    """Categoryモデルのシリアライザー"""

    # 型アノテーション: 更新時はCategoryインスタンス、作成時はNone
    instance: Optional[Category]

    class Meta:
        model = Category
        fields = ["id", "company", "name", "parent_category", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_name(self, value: str) -> str:
        """カテゴリ名のバリデーション"""
        if not value or not value.strip():
            raise serializers.ValidationError("カテゴリ名は必須です。")
        if len(value.strip()) > 255:
            raise serializers.ValidationError("カテゴリ名は255文字以内で入力してください。")
        return value.strip()

    def validate_parent_category(self, value: Optional[Category]) -> Optional[Category]:
        """親カテゴリのバリデーション"""
        if value is not None:
            # 親カテゴリが存在することを確認
            if not Category.objects.filter(id=value.id).exists():
                raise serializers.ValidationError("指定された親カテゴリが存在しません。")
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """全体のバリデーション"""
        company: Optional[Company] = attrs.get("company")
        name: Optional[str] = attrs.get("name")
        parent_category: Optional[Category] = attrs.get("parent_category")

        if self.instance:
            # 更新時: 同じ company + name の組み合わせが他に存在しないかチェック
            if company and name:
                existing = Category.objects.filter(
                    company=company, name=name
                ).exclude(id=self.instance.id) # 更新時は現在のインスタンスを除外
                if existing.exists():
                    raise serializers.ValidationError(
                        {"name": "この企業には既に同じ名前のカテゴリが存在します。"}
                    )
        else:
            # 作成時: company + name の一意性チェック
            if company and name:
                if Category.objects.filter(company=company, name=name).exists():
                    raise serializers.ValidationError(
                        {"name": "この企業には既に同じ名前のカテゴリが存在します。"}
                    )

        # 親カテゴリが同じ企業に属しているかチェック
        if parent_category and company:
            if parent_category.company != company:
                raise serializers.ValidationError(
                    {"parent_category": "親カテゴリは同じ企業に属している必要があります。"}
                )

        # 自己参照チェック（更新時）
        if self.instance and parent_category:
            if parent_category.id == self.instance.id:
                raise serializers.ValidationError(
                    {"parent_category": "カテゴリ自身を親カテゴリに設定することはできません。"}
                )

            # 循環参照チェック
            current = parent_category
            while current is not None:
                if current.id == self.instance.id:
                    raise serializers.ValidationError(
                        {"parent_category": "循環参照が発生するため、この親カテゴリは設定できません。"}
                    )
                current = current.parent_category

        return attrs
