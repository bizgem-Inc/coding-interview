from rest_framework import serializers

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
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("カテゴリ名は必須です。")
        return value

    def validate(self, attrs):
        company = attrs.get("company") or self.instance.company
        name = attrs.get("name") or self.instance.name
        parent = attrs.get("parent_category")

        # 同一企業内でカテゴリ名は一意
        qs = Category.objects.filter(company=company, name=name)
        # 更新時は自分自身を除外
        if self.instance:
            qs = qs.exclude(id=self.instance.id)

        if qs.exists():
            raise serializers.ValidationError(
                "同一企業内でカテゴリ名は一意である必要があります。"
            )

        # 親カテゴリは同一企業である必要がある
        if parent and parent.company_id != company.id:
            raise serializers.ValidationError(
                "親カテゴリは同一企業に属している必要があります。"
            )

        # 循環参照
        if parent and self.instance:
            current = parent
            while current is not None:
                if current == self.instance:
                    raise serializers.ValidationError(
                        "親カテゴリに自身または子孫カテゴリを指定することはできません。"
                    )
                current = current.parent_category

        return attrs