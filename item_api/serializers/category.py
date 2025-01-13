from typing import Optional

from rest_framework import serializers

from item_api.domain.category_factory import (
    CategoryDto,
    CategoryFactory,
    CategoryService,
)
from item_api.exception.custom_exceptions import (
    NoUpdateParameterException,
)
from item_api.models import Category
from item_api.serializers import DATE_TIME_FORMAT, validate_require


def validate_category_name(value: Optional[str]) -> str:
    validate_require(value=value, key_name="name", item_name="カテゴリ名")
    return str(value)


class CategorySerializer(serializers.Serializer):
    id = serializers.UUIDField(required=False, allow_null=True)
    company = serializers.UUIDField(required=False, allow_null=True)
    name = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )  # patch のみ必須であるようにするため。
    parent_category = serializers.UUIDField(required=False, allow_null=True)
    created_at = serializers.DateTimeField(required=False, format=DATE_TIME_FORMAT)
    updated_at = serializers.DateTimeField(required=False, format=DATE_TIME_FORMAT)

    def is_valid(self, *, raise_exception=False):
        request_method = self.context.get("request").method
        if request_method in ["POST", "PUT"]:
            if not self.initial_data.get("name"):
                raise NoUpdateParameterException("カテゴリ名")
            if not self.initial_data.get("company"):
                raise NoUpdateParameterException("企業ID")

        if request_method == "PATCH":
            if (
                not self.initial_data.get("name")
                and not self.initial_data.get("company")
                and not self.initial_data.get("parent_category")
            ):
                raise NoUpdateParameterException(
                    "カテゴリ名または企業IDまたは親カテゴリID"
                )

        return super().is_valid(raise_exception=raise_exception)

    def create(self, validated_data):
        category: Category = CategoryFactory.create_new_category(
            company_id=validated_data.get("company"),
            name=validated_data.get("name"),
            parent_category_id=validated_data.get("parent_category"),
        )
        category.save()
        return category

    def update(self, instance, validated_data):
        name = validated_data.get("name", None)
        company_id = validated_data.get("company")
        company_id = company_id if company_id is not None else instance.company.id

        original_category_id = (
            instance.parent_category.id
            if instance.parent_category is not None
            else None
        )
        method = self.context["request"].method

        if method == "PATCH":
            # name のみ指定されていない場合は重複チェックをおこわないので、None をいれる。。。
            parent_category_id = validated_data.get("parent_category")
            parent_category_id = (
                parent_category_id
                if parent_category_id is not None
                else original_category_id
            )
        else:
            parent_category_id = validated_data.get("parent_category")

        renewed_company, renewed_parent_category = CategoryService.validate_category(
            category=CategoryDto(
                name=name, company_id=company_id, parent_category_id=parent_category_id
            )
        )
        if name is not None:
            instance.name = name
        if company_id is not None:
            instance.company = renewed_company
        if parent_category_id is not None or method == "PUT":
            # PUT の場合は強制的に置き換えるので 親カテゴリIDは NULL でもセットさせる
            instance.parent_category = renewed_parent_category

        instance.save()
        return instance
