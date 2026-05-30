from rest_framework import serializers

from api.models.category import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "company", "name", "parent_category", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
        # UniqueConstraint由来の自動validatorと重複するため、重複チェックはvalidate()側に寄せる
        validators = []

    def validate(self, attrs):
        instance = getattr(self, "instance", None)

        company = attrs.get("company", instance.company if instance else None)
        name = attrs.get("name", instance.name if instance else None)
        parent_category = attrs.get("parent_category", instance.parent_category if instance else None)

        if company is not None and name is not None:
            qs = Category.objects.filter(company=company, name=name)
            if instance is not None:
                qs = qs.exclude(id=instance.id)
            if qs.exists():
                raise serializers.ValidationError({"name": "この企業には既に同じ名前のカテゴリが存在します。"})

        if parent_category is not None and company is not None and parent_category.company_id != company.id:
            raise serializers.ValidationError(
                {"parent_category": "親カテゴリは同じ企業のカテゴリである必要があります。"}
            )

        if instance is not None and parent_category is not None:
            if parent_category.id == instance.id:
                raise serializers.ValidationError(
                    {"parent_category": "自分自身を親カテゴリに設定することはできません。"}
                )

            current = parent_category
            while current is not None:
                if current.id == instance.id:
                    raise serializers.ValidationError(
                        {"parent_category": "子孫カテゴリを親カテゴリに設定することはできません。"}
                    )
                current = current.parent_category

        return attrs
