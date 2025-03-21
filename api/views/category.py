from uuid import UUID
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from api.repositories.category_repository import CategoryRepository


class CategoryViewSet(GenericViewSet):
    repository = CategoryRepository()

    def list(self, request: Request) -> Response:
        pass

    def retrieve(self, request: Request, category_id: UUID) -> Response:
        pass

    def create(self, request: Request) -> Response:
        pass

    def update(self, request: Request, category_id: UUID) -> Response:
        pass

    def destroy(self, request: Request, category_id: UUID) -> Response:
        pass
