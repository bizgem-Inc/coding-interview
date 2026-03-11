from django.http import Http404, HttpResponseBadRequest
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from api.models import Company, Category
from api.repository import CategoryRepository
from api.repository.company_repository import CompanyRepository
from api.serializers import CategorySerializer
from api.service import CategoryListService, CategoryRetrieveService, CategoryDestroyService, CategoryCreateService, \
    CategoryUpdateService


class CategoryViewSet(ViewSet):

    def list(self, request, company_id):

        try:
            categories = CategoryListService(CategoryRepository(), CompanyRepository()).handle(company_id)

        except Company.DoesNotExist:
            raise Http404("Company not found")

        return Response(CategorySerializer(categories, many=True).data)

    def retrieve(self, request, company_id, category_id):

        try:
            category = CategoryRetrieveService(CategoryRepository(), CompanyRepository()).handle(company_id, category_id)

        except Company.DoesNotExist:
            raise Http404("Company not found")

        except Category.DoesNotExist:
            raise Http404("Category not found")

        return Response(CategorySerializer(category, many=False).data)

    def create(self, request, company_id):
        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        category_create_service = CategoryCreateService(CategoryRepository(), CompanyRepository())

        try:
            category_create_service.handle(
                company_id=company_id,
                name=serializer.validated_data["name"],
                parent_category_id=serializer.validated_data.get("parent_category_id"),
            )

        except Company.DoesNotExist:
            raise NotFound("Company not found")

        except Category.DoesNotExist:
            raise NotFound("Parent category not found")

        return Response(status=status.HTTP_201_CREATED)

    def update(self, request, company_id, category_id):
        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        category_update_service = CategoryUpdateService(CategoryRepository(), CompanyRepository())

        try:
            category_update_service.handle(
                company_id=company_id,
                category_id=category_id,
                name=serializer.validated_data["name"],
                parent_category_id=serializer.validated_data.get("parent_category_id"),
            )

        except Company.DoesNotExist:
            raise NotFound("Company not found")

        return Response(status=status.HTTP_200_OK)

    def destroy(self, request, company_id, category_id):

        category_destroy_service = CategoryDestroyService(CategoryRepository(), CompanyRepository())

        try:
            category_destroy_service.handle(company_id, category_id)

        except Company.DoesNotExist:
            raise NotFound("Company not found")

        except Category.DoesNotExist:
            raise NotFound("Category not found")

        return Response(status=status.HTTP_204_NO_CONTENT)

