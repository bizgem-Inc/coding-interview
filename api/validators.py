from rest_framework import serializers
from api.models.category import Category


def assert_same_company(company, parent):
    """checking parent category"""
    if parent and company and parent.company_id != company.id:
        raise serializers.ValidationError(
            {"parent_category": "parent category should be the same"}
        )


def assert_no_self_parent(instance, parent):
    """checking self parent"""
    if instance is not None and parent is not None and instance.id == parent.id:
        raise serializers.ValidationError({"parent_category": "this is self parent"})


def assert_no_cycle(parent, current_id=None):
    """checking circular reference"""
    p = parent
    while p is not None:
        if current_id is not None and getattr(p, "id", None) == current_id:
            raise serializers.ValidationError(
                {"parent_category": "this is circular reference"}
            )
        p = getattr(p, "parent_category", None)


def assert_unique_name(company, name, exclude_id=None):
    """checking unique name within the company"""
    if not company or not name:
        return
    qs = Category.objects.filter(company=company, name=name)
    if exclude_id:
        qs = qs.exclude(id=exclude_id)
    if qs.exists():
        raise serializers.ValidationError(
            {"name": "This name is already used in this company."}
        )
