from rest_framework import serializers

from api.models import Category, Company


class CategorySerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        pk_field=serializers.UUIDField(format="hex_verbose"),
    )
    parent_category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        allow_null=True,
        required=False,
        pk_field=serializers.UUIDField(format="hex_verbose"),
    )

    class Meta:
        model = Category
        fields = ["id", "company", "name", "parent_category", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        if self.instance is not None and "company" in self.initial_data:
            raise serializers.ValidationError({"company": ["This field cannot be updated."]})

        company = attrs.get("company")
        if company is None and self.instance is not None:
            company = self.instance.company

        parent_category = attrs.get("parent_category", serializers.empty)
        if parent_category is serializers.empty:
            parent_category = self.instance.parent_category if self.instance is not None else None

        if parent_category is not None and company is not None and parent_category.company_id != company.id:
            raise serializers.ValidationError(
                {"parent_category": ["Parent category must belong to the same company."]}
            )

        name = attrs.get("name")
        if name is None and self.instance is not None:
            name = self.instance.name

        if company is not None and name:
            queryset = Category.objects.filter(company=company, name=name)
            if self.instance is not None:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError({"name": ["This name is already used in the company."]})

        return attrs
