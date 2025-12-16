from rest_framework import serializers
from api.models.category import Category

# Serializer for Category model to handle input/output for the API
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "company",
            "name",
            "parent_category",
            "created_at",
            "updated_at",
        ]
