from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.models import Category
from api.serializers.company import CompanySerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "company", "name", "parent_category", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
        validators = [
            UniqueTogetherValidator(
                queryset=Category.objects.all(),
                fields=["company", "name"],
            )
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["company"] = CompanySerializer(instance.company).data
        return representation
