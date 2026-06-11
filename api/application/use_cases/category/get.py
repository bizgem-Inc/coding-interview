from api.application.dto.category import CategoryResponse
from api.application.ports.category_repository import CategoryRepository
from api.domain.entities.category import Category
from api.domain.exceptions import CategoryNotFoundError
from api.domain.new_types.category_id import CategoryId


class GetCategory:
    """Category詳細取得ユースケース。"""

    def __init__(self, repository: CategoryRepository) -> None:
        self.repository = repository

    def execute(self, category_id: CategoryId) -> CategoryResponse:
        category = self.repository.find_by_id(category_id)
        if category is None:
            raise CategoryNotFoundError(category_id)
        return self._to_response(category)

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
