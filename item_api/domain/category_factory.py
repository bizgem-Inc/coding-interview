import uuid
from dataclasses import dataclass
from typing import Optional

from item_api.exception.custom_exceptions import ConflictedException
from item_api.models import Category, Company


@dataclass
class CategoryDto:
    company_id: Optional[uuid.UUID]
    name: Optional[str]
    parent_category_id: Optional[uuid.UUID]


class CategoryFactory:
    @staticmethod
    def create_new_category(
        company_id: uuid.UUID, name: str, parent_category_id: Optional[uuid.UUID]
    ) -> Category:
        """
        新規カテゴリを生成します
        """
        company, parent_category = CategoryService.validate_category(
            category=CategoryDto(
                company_id=company_id, name=name, parent_category_id=parent_category_id
            )
        )
        return Category(company=company, name=name, parent_category=parent_category)


class CategoryService:
    @staticmethod
    def validate_category(category: CategoryDto) -> tuple[Company, Optional[Category]]:
        """
        カテゴリが妥当であるかを判断します。妥当である場合、企業、親カテゴリを返します。
        """
        try:
            company: Company = Company.objects.get(pk=category.company_id)
        except Company.DoesNotExist:
            raise ConflictedException(
                message=f"{category.company_id}は存在しない企業IDです。存在する企業を指定してください。"
            )

        if category.name is not None:
            CategoryService._is_valid_company_category(
                company_id=category.company_id, name=category.name
            )
        parent_category = None
        if category.parent_category_id is not None:
            try:
                parent_category = Category.objects.get(pk=category.parent_category_id)
            except Category.DoesNotExist:
                raise ConflictedException(
                    f"親カテゴリ[{category.parent_category_id}]は存在していません"
                )

            if not parent_category.company.id == category.company_id:
                raise ConflictedException(
                    f"指定した親カテゴリidは[{category.company_id}]のカテゴリではありません"
                )

        return company, parent_category

    @staticmethod
    def _is_valid_company_category(company_id: uuid.UUID, name: str) -> bool:
        try:
            ## 企業内でカテゴリはユニークであること
            Category.objects.get(
                company=company_id,
                name=name,
            )
        except Category.DoesNotExist:
            return True

        raise ConflictedException(f"{name}はすでに登録済みのカテゴリです")
