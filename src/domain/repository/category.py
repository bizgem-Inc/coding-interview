from abc import ABC, abstractmethod
from uuid import UUID
from typing import List

from domain.entity.category import CategoryEntity


class ICategoryRepository(ABC):
    @abstractmethod
    def fetch(self, id: UUID) -> CategoryEntity:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> List[CategoryEntity]:
        raise NotImplementedError

    @abstractmethod
    def create(self, category: CategoryEntity):
        raise NotImplementedError

    @abstractmethod
    def update(self, category: CategoryEntity):
        raise NotImplementedError

    @abstractmethod
    def delete(self, id):
        raise NotImplementedError
