from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.models.category import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "company", "name", "parent_category", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {"parent_category": {"required": False}}
        validators = [
            UniqueTogetherValidator(
                queryset=Category.objects.all(),
                fields=["company", "name"],
            )
        ]

    def validate(self, attrs):
        instance = self.instance
        company = attrs.get("company", instance.company if instance else None)
        parent = attrs.get("parent_category", instance.parent_category if instance else None)

        if parent is not None:
            if parent.company_id != company.pk:
                raise serializers.ValidationError(
                    {"parent_category": "Parent category must belong to the same company."}
                )
            ancestor = parent
            visited = set()
            while ancestor is not None:
                if (instance and ancestor.pk == instance.pk) or ancestor.pk in visited:
                    raise serializers.ValidationError(
                        {"parent_category": "Parent category must not create a cycle."}
                    )
                visited.add(ancestor.pk)
                ancestor = ancestor.parent_category

        if instance and company.pk != instance.company_id:
            if Category.objects.filter(parent_category=instance).exclude(company=company).exists():
                raise serializers.ValidationError(
                    {"company": "Company must match the category's children."}
                )

        return attrs
