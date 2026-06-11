from api.application.ports.category_repository import CategoryRepository
from api.domain.exceptions import CategoryNotFoundError
from api.domain.new_types.category_id import CategoryId


class DeleteCategory:
    """Category削除ユースケース。"""

    def __init__(self, repository: CategoryRepository) -> None:
        self.repository = repository

    def execute(self, category_id: CategoryId) -> None:
        existing = self.repository.find_by_id(category_id)
        if existing is None:
            raise CategoryNotFoundError(category_id)
        self.repository.delete(category_id)
