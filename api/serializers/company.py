from rest_framework import serializers

from api.models import Company


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            'name',
            'created_at',
            'updated_at'
        )
