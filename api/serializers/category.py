from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "company", "name", "parent_category", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
        validators = [
            # DRF 3.14 は Meta.constraints の UniqueConstraint を自動検出しないため明示する
            UniqueTogetherValidator(
                queryset=Category.objects.all(),
                fields=["company", "name"],
                message="同じ企業内に同名のカテゴリが既に存在します。",
            )
        ]

    def validate(self, attrs):
        # PATCH では attrs に含まれないフィールドがあるため、既存インスタンスの値で補う
        instance = self.instance
        company = attrs.get("company", getattr(instance, "company", None))
        parent = attrs.get("parent_category", getattr(instance, "parent_category", None))

        if parent is None:
            return attrs

        if parent.company_id != company.id:
            raise serializers.ValidationError({"parent_category": "親カテゴリは同じ企業のカテゴリを指定してください。"})

        if instance is not None:
            self._validate_no_cycle(instance, parent)

        return attrs

    @staticmethod
    def _validate_no_cycle(instance, parent):
        # 自分自身や自分の子孫を親にすると循環参照になるため、親を辿って検査する
        node = parent
        while node is not None:
            if node.pk == instance.pk:
                raise serializers.ValidationError({"parent_category": "自分自身またはその子孫を親カテゴリに指定することはできません。"})
            node = node.parent_category
