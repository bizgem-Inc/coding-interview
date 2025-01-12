from rest_framework import serializers
from  item_api.models import Company


class CompanySerializer(serializers.Serializer):
    name = serializers.CharField()

    def validate_name(self, value):
        """nameフィールドのカスタムバリデーション"""
        if not value.strip():
            raise serializers.ValidationError("Name cannot be empty or just whitespace.")
        return value


    def create(self, validated_data: dict[str, str]):
        company = Company(**validated_data)
        company.save()
        return company

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.save()
        return instance

