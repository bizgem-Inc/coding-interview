from datetime import datetime, timezone
from uuid import uuid4

from api.application.dto.category import CategoryResponse, CreateCategoryRequest
from api.application.ports.category_repository import CategoryRepository
from api.domain.entities.category import Category
from api.domain.exceptions import (
    CompanyNotFoundError,
    DuplicateCategoryNameError,
    ReferencedCategoryNotFoundError,
)
from api.domain.new_types.category_id import CategoryId
from api.domain.new_types.company_id import CompanyId


class CreateCategory:
    """Category作成ユースケース。"""

    def __init__(self, repository: CategoryRepository) -> None:
        self.repository = repository

    def execute(self, request: CreateCategoryRequest) -> CategoryResponse:
        # Companyの存在確認
        if not self.repository.company_exists(request.company_id):
            raise CompanyNotFoundError(request.company_id)

        # 親Categoryの存在確認
        if request.parent_category_id is not None:
            parent = self.repository.find_parent_by_id(request.parent_category_id)
            if parent is None:
                raise ReferencedCategoryNotFoundError(request.parent_category_id)

        # 同一Company内の名前重複チェック
        existing = self.repository.find_by_company_and_name(
            request.company_id, request.name
        )
        if existing is not None:
            raise DuplicateCategoryNameError(request.name, request.company_id)

        now = datetime.now(timezone.utc)
        new_category = Category(
            id=CategoryId(uuid4()),
            company_id=request.company_id,
            name=request.name,
            parent_category_id=request.parent_category_id,
            created_at=now,
            updated_at=now,
        )

        saved = self.repository.save(new_category)
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
