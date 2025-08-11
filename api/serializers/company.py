from rest_framework import serializers

from api.models import Company
from api.serializers.category import CategorySerializer

class CompanySerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    class Meta:
        model = Company
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
