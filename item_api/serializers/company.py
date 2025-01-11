from rest_framework import serializers
from  item_api.models import Company


class CompanySerializer(serializers.Serializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].error_messages = {'required': '会社名は必須項目です'}


class CompanyCreateSerializer(CompanySerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    id = serializers.UUIDField(required=False)
    name = serializers.CharField()
    created_at = serializers.DateTimeField(required=False)
    updated_at = serializers.DateTimeField(required=False)


    def create(self, validated_data: dict[str, str]):
        company = Company(name = validated_data.get("name"))
        company.save()
        return company


class CompanyUpdateSerializer(CompanySerializer):
    def update(self, instance, validated_data):
        instance.name = validated_data.get("name")
        instance.save()
        return instance
