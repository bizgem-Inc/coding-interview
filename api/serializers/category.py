from rest_framework import serializers

from api.models.category import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "company", "name", "parent_category", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_name(self, value):
        name = value.strip()
        if not name:
            raise serializers.ValidationError("Category name cannot be blank.")
        return name

    def validate(self, attrs):
        company = attrs.get("company", getattr(self.instance, "company", None))
        parent_category = attrs.get("parent_category", getattr(self.instance, "parent_category", None))
        name = attrs.get("name", getattr(self.instance, "name", None))

        if parent_category is not None and company is not None and parent_category.company_id != company.id:
            raise serializers.ValidationError({"parent_category": "Parent category must belong to the same company."})

        if self.instance is not None:
            self._validate_parent_chain(parent_category)
            self._validate_child_companies(company)

        if company is not None and name:
            queryset = Category.objects.filter(company=company, name=name)
            if self.instance is not None:
                queryset = queryset.exclude(id=self.instance.id)
            if queryset.exists():
                raise serializers.ValidationError({"name": "Category name must be unique within the company."})

        return attrs

    def _validate_parent_chain(self, parent_category):
        checked_category_ids = set()
        while parent_category is not None:
            if parent_category.id == self.instance.id:
                raise serializers.ValidationError({"parent_category": "Category cannot be its own ancestor."})
            if parent_category.id in checked_category_ids:
                return

            checked_category_ids.add(parent_category.id)
            parent_category = parent_category.parent_category

    def _validate_child_companies(self, company):
        if company is None:
            return

        has_child_from_other_company = (
            Category.objects.filter(parent_category=self.instance).exclude(company=company).exists()
        )
        if has_child_from_other_company:
            raise serializers.ValidationError(
                {"company": "Category with child categories cannot move to another company."}
            )
