from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "company",
            "name",
            "parent_category",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
        validators = [
            UniqueTogetherValidator(
                queryset=Category.objects.all(),
                fields=("company", "name"),
                message="A category with this company and name already exists.",
            )
        ]

    def validate_name(self, value):
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("This field may not be blank.")
        return stripped

    def validate(self, attrs):
        instance = self.instance

        if instance is None:
            company = attrs.get("company")
            parent = attrs.get("parent_category")
        else:
            company = attrs.get("company", instance.company)
            if "parent_category" in attrs:
                parent = attrs["parent_category"]
            else:
                parent = instance.parent_category

        if parent is not None:
            if parent.company_id != company.pk:
                raise serializers.ValidationError(
                    {"parent_category": "Parent category must belong to the same company."}
                )

        if instance is not None and parent is not None:
            if parent.pk == instance.pk:
                raise serializers.ValidationError(
                    {"parent_category": "A category cannot be its own parent."}
                )
            # Traverse ancestors to prevent circular parent references.
            ancestor = parent
            visited = set()
            while ancestor is not None:
                if ancestor.pk == instance.pk:
                    raise serializers.ValidationError(
                        {"parent_category": "Cannot assign a descendant category as parent."}
                    )
                if ancestor.pk in visited:
                    break
                visited.add(ancestor.pk)
                ancestor = ancestor.parent_category

        return attrs
