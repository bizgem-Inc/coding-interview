from rest_framework import serializers

from api.models.category import Category


class CategorySerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        company = attrs.get("company", getattr(self.instance, "company", None))
        parent_category = attrs.get(
            "parent_category",
            getattr(self.instance, "parent_category", None),
        )

        if parent_category is None:
            return attrs

        if self.instance and parent_category.id == self.instance.id:
            raise serializers.ValidationError(
                {"parent_category": "A category cannot be its own parent."}
            )

        if company and parent_category.company_id != company.id:
            raise serializers.ValidationError(
                {"parent_category": "Parent category must belong to the same company."}
            )

        ancestor = parent_category
        visited_category_ids = set()
        while ancestor:
            if ancestor.id in visited_category_ids:
                raise serializers.ValidationError(
                    {"parent_category": "Parent category contains a circular reference."}
                )
            visited_category_ids.add(ancestor.id)

            if self.instance and ancestor.id == self.instance.id:
                raise serializers.ValidationError(
                    {"parent_category": "A category cannot use its descendant as parent."}
                )
            ancestor = ancestor.parent_category

        return attrs

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
        read_only_fields = ["id", "created_at", "updated_at"]
