from uuid import UUID
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from api.repositories.category_repository import CategoryRepository
from api.serializers.category import (
    CategoryGetAPIResponseSerializer,
    CategoryListAPIResponseSerializer,
    CategoryPatchAPIRequestSerializer,
    CategoryPostAPIRequestSerializer,
    CategoryPostAPIResponseSerializer,
)


class CategoryViewSet(GenericViewSet):
    repository = CategoryRepository()

    def list(self, request: Request) -> Response:
        categories = self.repository.get_categories(request.query_params["company_id"])
        serializer = CategoryListAPIResponseSerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request: Request, category_id: UUID) -> Response:
        category = self.repository.get_category_by_id(category_id)
        serializer = CategoryGetAPIResponseSerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request: Request) -> Response:
        serializer = CategoryPostAPIRequestSerializer(data=request.data)
        if serializer.is_valid():
            category = self.repository.create_category(
                company_id=serializer.validated_data["company_id"],
                name=serializer.validated_data["name"],
                parent_category_id=serializer.validated_data.get("parent_category_id"),
            )
            return Response(
                CategoryPostAPIResponseSerializer(category).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request: Request, category_id: UUID) -> Response:
        serializer = CategoryPatchAPIRequestSerializer(data=request.data)
        if serializer.is_valid():
            parent_category_id = (
                {"parent_category_id": serializer.validated_data["parent_category_id"]}
                if "parent_category_id" in serializer.validated_data
                else {}
            )
            self.repository.update_category(
                category_id=category_id,
                name=serializer.validated_data["name"],
                **parent_category_id,
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request: Request, category_id: UUID) -> Response:
        self.repository.delete_category(category_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
