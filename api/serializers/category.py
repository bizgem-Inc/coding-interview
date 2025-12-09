from rest_framework import serializers

from api.models.category import Category
from api.models.company import Company


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "company", "name", "parent_category", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_company(self, value):
        """Validate that the company exists."""
        if value and not Company.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Company does not exist.")
        return value

    def validate(self, attrs):
        """Validate the combination of company and name uniqueness, and parent category."""
        company = attrs.get("company")
        name = attrs.get("name")
        parent_category = attrs.get("parent_category")
        
        # For updates, use existing company if not provided
        if self.instance and company is None:
            company = self.instance.company
        
        # Check for unique company + name combination
        if company and name:
            queryset = Category.objects.filter(company=company, name=name)
            # Exclude current instance if updating
            if self.instance:
                queryset = queryset.exclude(id=self.instance.id)
            
            if queryset.exists():
                raise serializers.ValidationError(
                    {"name": "A category with this name already exists for this company."}
                )
        
        # Validate parent category belongs to same company
        if parent_category is not None and company:
            if parent_category.company_id != company.id:
                raise serializers.ValidationError(
                    {"parent_category": "Parent category must belong to the same company."}
                )
        
        return attrs

