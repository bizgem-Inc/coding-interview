from rest_framework import serializers
from api.models.category import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

    # validate the 'name' field
    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("category name cannot be empty.")
        return value

    # validate multiple fields at once
    def validate(self, attrs: dict):
        company = attrs.get("company", None)
        name = attrs.get("name", None)
        parent = attrs.get("parent_category", None)

        current_instance = self.instance if self.instance else None

        # check uniqueness of name within company
        if (
            Category.objects.filter(company=company, name=name)
            .exclude(id=current_instance.id)
            .exists()
        ):
            raise serializers.ValidationError(
                "A category with this name already exists in this company."
            )

        # check that parent category belongs to the same company
        if parent and parent.company != company:
            raise serializers.ValidationError(
                "Parent category must belong to the same company."
            )

        # parent cannot be itself
        if parent and current_instance.id and (parent.id == current_instance.id):
            raise serializers.ValidationError("A category cannot be its own parent.")

        return attrs
