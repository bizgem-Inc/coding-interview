from rest_framework import serializers
from api.models.category import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        company = attrs.get("company", getattr(self.instance, "company", None))
        parent = attrs.get("parent_category", getattr(self.instance, "parent_category", None))

        if parent and company and parent.company_id != company.id:
            raise serializers.ValidationError(
                {"parent_category": "Parent category must belong to the same company."}
            )

        if self.instance and parent and parent.id == self.instance.id:
            raise serializers.ValidationError(
                {"parent_category": "A category cannot be its own parent."}
            )

        return attrs
