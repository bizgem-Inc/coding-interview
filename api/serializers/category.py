from django.db import IntegrityError
from rest_framework import serializers

from api.models.category import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "company", "name", "parent_category", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {"parent_category": {"required": False, "allow_null": True}}

    def validate_name(self, value):
        normalized = value.strip()
        if not normalized:
            raise serializers.ValidationError("name must not be blank.")
        return normalized

    def validate(self, attrs):
        instance = self.instance
        company = attrs.get("company", instance.company if instance else None)
        name = attrs.get("name", instance.name if instance else None)
        parent_category = attrs.get("parent_category", instance.parent_category if instance else None)

        if company and name:
            existing = Category.objects.filter(company=company, name=name)
            if instance:
                existing = existing.exclude(pk=instance.pk)
            if existing.exists():
                raise serializers.ValidationError({"name": "name must be unique within the same company."})

        if parent_category is not None:
            if instance and parent_category.pk == instance.pk:
                raise serializers.ValidationError({"parent_category": "parent_category cannot be self."})
            if company and parent_category.company_id != company.id:
                raise serializers.ValidationError({"parent_category": "parent_category must belong to the same company."})

        return attrs

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError as exc:
            self._raise_validation_error_on_duplicate_name(exc)

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except IntegrityError as exc:
            self._raise_validation_error_on_duplicate_name(exc)

    def _raise_validation_error_on_duplicate_name(self, exc):
        message = str(exc).lower()
        # 同時書き込み時は事前チェックをすり抜けることがあるため、DBの一意制約違反を補足してハンドリングする。
        if "unique_company_category_combination" in message or "duplicate key value violates unique constraint" in message:
            raise serializers.ValidationError({"name": "name must be unique within the same company."}) from exc
        raise exc
