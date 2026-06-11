from api.application.dto.category import CategoryResponse
from api.application.ports.category_repository import CategoryRepository
from api.domain.entities.category import Category


class ListCategories:
    """Category一覧取得ユースケース。"""

    def __init__(self, repository: CategoryRepository) -> None:
        self.repository = repository

    def execute(self, limit: int = 10, offset: int = 0) -> list[CategoryResponse]:
        categories = self.repository.find_all(limit=limit, offset=offset)
        return [self._to_response(c) for c in categories]

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
