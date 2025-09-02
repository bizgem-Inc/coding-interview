from rest_framework import serializers
from api.models.category import Category
from api import validators as cat_validators


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs):
        """
        Checking parent category company matches / self-references / circular references /
        duplicate names within the company
        """
        instance = getattr(self, "instance", None)

        # if values are not sent, existing values are used
        company = (
            attrs.get("company")
            if "company" in attrs
            else (instance.company if instance else None)
        )
        parent = (
            attrs.get("parent_category")
            if "parent_category" in attrs
            else (instance.parent_category if instance else None)
        )
        name = (
            attrs.get("name")
            if "name" in attrs
            else (instance.name if instance else None)
        )
        cur_id = getattr(instance, "id", None)

        # validation
        cat_validators.assert_same_company(company, parent)
        cat_validators.assert_no_self_parent(instance, parent)
        cat_validators.assert_no_cycle(parent, cur_id)
        cat_validators.assert_unique_name(company, name, exclude_id=cur_id)

        return attrs
