from rest_framework import serializers
from ..models.category import Category

class ApiCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'company', 'name', 'parent_category', 'created_at', 'updated_at')
