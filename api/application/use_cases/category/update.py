from datetime import datetime, timezone

from api.application.dto.category import CategoryResponse, UpdateCategoryRequest
from api.application.ports.category_repository import CategoryRepository
from api.domain.entities.category import Category
from api.domain.exceptions import (
    CategoryNotFoundError,
    CompanyNotFoundError,
    DuplicateCategoryNameError,
    ReferencedCategoryNotFoundError,
)
from api.domain.new_types.category_id import CategoryId


class UpdateCategory:
    """Category更新ユースケース。"""

    def __init__(self, repository: CategoryRepository) -> None:
        self.repository = repository

    def execute(
        self, category_id: CategoryId, request: UpdateCategoryRequest
    ) -> CategoryResponse:
        existing = self.repository.find_by_id(category_id)
        if existing is None:
            raise CategoryNotFoundError(category_id)

        # Companyの存在確認
        if not self.repository.company_exists(request.company_id):
            raise CompanyNotFoundError(request.company_id)

        # 親Categoryの存在確認
        if request.parent_category_id is not None:
            parent = self.repository.find_parent_by_id(request.parent_category_id)
            if parent is None:
                raise ReferencedCategoryNotFoundError(request.parent_category_id)

        # 同一Company内の名前重複チェック（自身は除外）
        duplicate = self.repository.find_by_company_and_name(
            request.company_id, request.name
        )
        if duplicate is not None and duplicate.id != category_id:
            raise DuplicateCategoryNameError(request.name, request.company_id)

        now = datetime.now(timezone.utc)
        updated = Category(
            id=existing.id,
            company_id=request.company_id,
            name=request.name,
            parent_category_id=request.parent_category_id,
            created_at=existing.created_at,
            updated_at=now,
        )

        saved = self.repository.save(updated)
        return self._to_response(saved)

    @staticmethod
    def _to_response(category: Category) -> CategoryResponse:
        return CategoryResponse(
            id=category.id,
            company_id=category.company_id,
            name=category.name,
            parent_category_id=category.parent_category_id,
            created_at=category.created_at,
            updated_at=category.updated_at,
        )
