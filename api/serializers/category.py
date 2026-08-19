from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.models.category import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "company", "name", "parent_category", "created_at", "updated_at"]
        validators = [UniqueTogetherValidator(queryset=Category.objects.all(), fields=["company", "name"])]

    def validate(self, attrs):
        company = attrs.get("company", self.instance.company if self.instance else None)
        parent_category = attrs.get("parent_category", self.instance.parent_category if self.instance else None)

        if parent_category is None:
            return attrs

        if parent_category == self.instance:
            raise serializers.ValidationError({"parent_category": "A category cannot be its own parent category."})

        if parent_category.company_id != company.id:
            raise serializers.ValidationError({"parent_category": "The parent category must belong to the same company."})

        return attrs
