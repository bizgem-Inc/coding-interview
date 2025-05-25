from rest_framework import serializers

from api.models import Category

class CategoryWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'company', 'name', 'parent_category')

class CategoryReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'company', 'name', 'parent_category')
        depth = 1
