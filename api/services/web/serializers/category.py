from rest_framework import serializers

from api.domain.new_types.category_id import CategoryId
from api.domain.new_types.company_id import CompanyId
from api.domain.exceptions import (
    CategoryNotFoundError,
    CompanyNotFoundError,
    DuplicateCategoryNameError,
    ReferencedCategoryNotFoundError,
)


class CategoryInputSerializer(serializers.Serializer):
    """Category作成・更新の入力検証。"""

    company_id = serializers.UUIDField()
    name = serializers.CharField(max_length=255)
    parent_category_id = serializers.UUIDField(required=False, allow_null=True)

    def validate_name(self, value: str) -> str:
        if len(value) > 255:
            raise serializers.ValidationError("Name must not exceed 255 characters.")
        return value

    def to_domain_ids(self) -> dict:  # type: ignore[override]
        data = self.validated_data  # type: ignore[assignment]
        return {
            "company_id": CompanyId(data["company_id"]),  # type: ignore[index]
            "name": data["name"],  # type: ignore[index]
            "parent_category_id": CategoryId(data["parent_category_id"])
            if data.get("parent_category_id")  # type: ignore[union-attr]
            else None,
        }


class CategoryPartialInputSerializer(serializers.Serializer):
    """Category部分更新の入力検証。

    明示的なnullはrejectし、省略のみを許可する。
    """

    company_id = serializers.UUIDField(required=False, allow_null=False)
    name = serializers.CharField(max_length=255, required=False, allow_null=False)
    parent_category_id = serializers.UUIDField(required=False, allow_null=True)

    def validate_name(self, value: str) -> str:
        if len(value) > 255:
            raise serializers.ValidationError("Name must not exceed 255 characters.")
        return value


class CategoryOutputSerializer(serializers.Serializer):
    """Category出力シリアライザー。"""

    id = serializers.UUIDField()
    company_id = serializers.UUIDField()
    name = serializers.CharField()
    parent_category_id = serializers.UUIDField(allow_null=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


def handle_domain_error(exc: Exception) -> serializers.ValidationError:
    """ドメイン例外をDRFのValidationErrorへ変換する。"""
    if isinstance(exc, CategoryNotFoundError):
        return serializers.ValidationError(
            {"detail": str(exc)}, code="not_found"
        )
    if isinstance(exc, ReferencedCategoryNotFoundError):
        return serializers.ValidationError(
            {"parent_category_id": [str(exc)]}, code="not_found"
        )
    if isinstance(exc, CompanyNotFoundError):
        return serializers.ValidationError(
            {"company_id": [str(exc)]}, code="not_found"
        )
    if isinstance(exc, DuplicateCategoryNameError):
        return serializers.ValidationError(
            {"name": [str(exc)]}, code="duplicate"
        )
    raise exc
