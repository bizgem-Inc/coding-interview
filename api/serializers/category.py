from rest_framework import serializers
from api.models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "company","name", "parent_category", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("カテゴリ名は必須です")
        return value.strip()

    def validate(self, attrs):
        company = attrs.get("company")
        name = attrs.get("name")
        if company and name:
            queryset = Category.objects.filter(company=company, name=name.strip())
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError(
                    {"name": "この企業では既に同じカテゴリ名が存在します"}
                )
        return attrs
