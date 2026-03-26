from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.models import Category


class CategorySerializer(serializers.ModelSerializer):
    # 入力では `parent_category` に UUID を渡し、保存前に参照先オブジェクトへ解決する。
    parent_category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Category
        fields = [
            "id",
            "company",
            "name",
            "parent_category",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        validators = [
            UniqueTogetherValidator(
                queryset=Category.objects.all(),
                fields=("company", "name"),
            )
        ]

    def validate_name(self, value: str) -> str:
        # 見た目の差異（前後スペース）を吸収し、空文字は弾く。
        value = value.strip()
        if not value:
            raise serializers.ValidationError("カテゴリ名は必須です。")
        return value

    def validate(self, attrs):
        # `PATCH`（partial_update）では必須フィールドが落ちることがあるため、
        # 参照整合性チェックに必要な値は instance 側から補って行う。
        company = attrs.get("company", getattr(self.instance, "company", None))
        parent = attrs.get(
            "parent_category",
            getattr(self.instance, "parent_category", None),
        )

        # 参照整合性チェックに必要な値が揃っていない場合は、DRF の通常エラーに任せる。
        if parent is not None and company is not None:
            if parent.company_id != company.id:
                raise serializers.ValidationError(
                    {"parent_category": "親カテゴリは同一の company に属している必要があります。"}
                )

            # 自身を親にすると循環参照の入口になるため禁止する。
            if self.instance is not None and parent.id == self.instance.id:
                raise serializers.ValidationError(
                    {"parent_category": "親カテゴリに自身は指定できません。"}
                )

        return attrs
