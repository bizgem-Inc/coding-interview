from rest_framework import serializers
from api.models.category import Category


def _validate_parent_same_company(parent_category, company):
    if parent_category and company and parent_category.company_id != company.id:
        raise serializers.ValidationError(
            {"parent_category": "parent_category must belong to the same company."}
        )


def _validate_not_self_parent(instance, parent_category):
    if instance and parent_category and parent_category.pk == instance.pk:
        raise serializers.ValidationError(
            {"parent_category": "A category cannot be its own parent."}
        )


def _validate_no_cycle(instance, parent_category, *, max_steps: int = 100):
    if not (instance and parent_category):
        return

    visited = set()
    cur = parent_category
    steps = 0

    while cur:
        if cur.pk in visited:
            raise serializers.ValidationError(
                {"parent_category": "Detected a cycle in the category hierarchy."}
            )
        visited.add(cur.pk)

        if cur.pk == instance.pk:
            raise serializers.ValidationError(
                {"parent_category": "Cannot set a category's parent to its own descendant."}
            )

        cur = cur.parent_category
        steps += 1
        if steps > max_steps:
            raise serializers.ValidationError(
                {"parent_category": f"Hierarchy exceeds {max_steps} layers."}
            )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        instance = getattr(self, "instance", None)
        company = attrs.get("company", getattr(instance, "company", None))
        parent_category = attrs.get("parent_category", getattr(instance, "parent_category", None))

        _validate_parent_same_company(parent_category, company)
        _validate_not_self_parent(instance, parent_category)
        _validate_no_cycle(instance, parent_category)

        return attrs

    def get_fields(self):
        """
        On create: (no instance) company must be provided.
        On update: it’s optional, and we’ll ignore any change.
        """
        fields = super().get_fields()
        fields["company"].required = (self.instance is None)
        return fields

    def update(self, instance, validated_data):
        """
        Ignore attempts to change company on update (PUT/PATCH).
        """
        validated_data.pop("company", None)
        return super().update(instance, validated_data)
