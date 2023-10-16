from rest_framework import serializers
from ..models.category import Category
from ..models.company import Company

class ApiCompanySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Company
        fields = ('name')

class ApiCategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'company', 'name', 'parent_category', 'created_at', 'updated_at')

