from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import serializers

from api.models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "company", "name", "parent_category", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        if self.instance is None:
            instance = Category(**attrs)
        else:
            instance = self.instance
            for key, value in attrs.items():
                setattr(instance, key, value)

        try:
            instance.full_clean(validate_unique=False)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        return attrs
