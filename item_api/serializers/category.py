from typing import Optional

from rest_framework import serializers

from item_api.domain.category_factory import CategoryFactory, CategoryService, CategoryDto
from item_api.exception.custom_exceptions import RequiredException, NoUpdateParameterException, \
    AllSameUpdateParameterException
from item_api.models import Category
from item_api.serializers import DATE_TIME_FORMAT, validate_require


def validate_category_name(value: Optional[str]) -> str:
    validate_require(
        value=value,
        key_name='name',
        item_name='カテゴリ名'
    )
    return str(value)


class CategorySerializer(serializers.Serializer):
    id = serializers.UUIDField(required=False)
    company = serializers.UUIDField(required=False)
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True)  # patch のみ必須であるようにするため。
    parent_category = serializers.UUIDField(required=False, allow_null=True)
    created_at = serializers.DateTimeField(required=False, format=DATE_TIME_FORMAT)
    updated_at = serializers.DateTimeField(required=False, format=DATE_TIME_FORMAT)

    def is_valid(self, *, raise_exception=False):

        request_method = self.context.get("request").method
        if request_method in  ['POST', 'PATCH']:
            if not self.initial_data.get('name') and not self.initial_data.get('company'):
                raise NoUpdateParameterException('企業名または親カテゴリ')

        if request_method == 'PATCH':
            if not self.initial_data['company']:
                raise RequiredException(item_name='企業')

        return super().is_valid(raise_exception=raise_exception)

    def create(self, validated_data):
        category: Category = CategoryFactory.create_new_category(
            company_id=validated_data.get('company'),
            name=validated_data.get('name'),
            parent_category_id=validated_data.get('parent_category')
        )
        category.save()
        return category

    def update(self, instance, validated_data):

        name = validated_data.get('name', instance.name)
        company_id=validated_data.get('company', instance.company.id),
        original_parent_category_id = instance.parent_category.id if instance.parent_category is not None else None
        parent_category_id=validated_data.get('parent_category', original_parent_category_id)

        if name == instance.name and company_id == instance.company.id and parent_category_id == original_parent_category_id:
            raise AllSameUpdateParameterException()

        renewed_company, renewed_parent_category = CategoryService.validate_category(
            category=CategoryDto(
                name=name,
                company_id=company_id,
                parent_category_id=parent_category_id
            )
        )
        instance.name = name
        instance.company = renewed_company
        instance.parent_category = renewed_parent_category
        instance.save()
        return instance
