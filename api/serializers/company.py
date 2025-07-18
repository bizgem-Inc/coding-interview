from rest_framework import serializers
from api.models.company import Company
class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('id', 'name', 'created_at', 'updated_at')