import uuid
from typing import Optional

from . import DATE_TIME_FORMAT, validate_require
from item_api.models import Company, Category
from rest_framework import serializers

from item_api.exception.custom_exceptions import ConflictedException

def validate_company_name(value: Optional[str]) -> str:
    validate_require(
        value=value,
        key_name='name',
        item_name='企業名'
    )
    return value

class CompanySerializer(serializers.Serializer):
    id = serializers.UUIDField(required=False)
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True)  # patch のみ必須であるようにするため。
    created_at = serializers.DateTimeField(required=False, format=DATE_TIME_FORMAT)
    updated_at = serializers.DateTimeField(required=False, format=DATE_TIME_FORMAT)

    def is_valid(self, raise_exception=False):
        is_valid = super().is_valid(raise_exception=raise_exception)
        request_method = self.context.get("request").method
        if request_method in ['PATCH', 'POST']:
            validate_company_name(
                value=self.initial_data.get('name', None)
            )
        return is_valid

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name")
        instance.save()
        return instance

    def create(self, validated_data: dict[str, str]):
        company = Company(name=validated_data.get("name"))
        company.save()
        return company
