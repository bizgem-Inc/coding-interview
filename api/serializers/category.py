from rest_framework import serializers

from api.models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "company", "name", "parent_category", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")
        extra_kwargs = {"parent_category": {"required": False}}

    def validate(self, attrs):
        instance = self.instance
        company = attrs.get("company", instance.company if instance else None)
        name = attrs.get("name", instance.name if instance else None)
        parent = attrs.get("parent_category", instance.parent_category if instance else None)

        duplicates = Category.objects.filter(company=company, name=name)
        if instance:
            duplicates = duplicates.exclude(pk=instance.pk)
        if duplicates.exists():
            raise serializers.ValidationError({"name": "This name already exists for this company."})

        if parent:
            if parent.company_id != company.pk:
                raise serializers.ValidationError({"parent_category": "The parent must belong to the same company."})
            # Follow ancestors so a category cannot become its own descendant.
            ancestor = parent
            visited = set()
            while ancestor:
                if ancestor.pk in visited or (instance and ancestor.pk == instance.pk):
                    raise serializers.ValidationError({"parent_category": "Category hierarchies cannot contain cycles."})
                visited.add(ancestor.pk)
                ancestor = ancestor.parent_category

        if instance and instance.company_id != company.pk:
            if Category.objects.filter(parent_category=instance).exclude(company=company).exists():
                raise serializers.ValidationError({"company": "The company must match existing child categories."})

        return attrs
