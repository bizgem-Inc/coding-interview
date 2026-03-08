from django.http import Http404, HttpResponseBadRequest
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from api.repository import CategoryRepository
from api.serializers import CategorySerializer
from api.service import CategoryListService, CategoryRetrieveService, CategoryDestroyService, CategoryCreateService


class CategoryViewSet(ViewSet):

    def list(self, request, company_id):

        categories = CategoryListService(CategoryRepository()).handle(company_id)

        return Response(CategorySerializer(categories, many=True).data)

    def retrieve(self, request, company_id, category_id):

        category = CategoryRetrieveService(CategoryRepository()).handle(company_id, category_id)

        if category is None:
            raise Http404("Category not found")

        return Response(CategorySerializer(category, many=False).data)

    def create(self, request, company_id):
        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        category_create_service = CategoryCreateService(CategoryRepository())

        try:
            category = category_create_service.handle(
                company_id=company_id,
                name=serializer.validated_data["name"],
                parent_category_id=serializer.validated_data.get("parent_category_id"),
            )

        except NotFound as e:
            raise Http404(str(e.detail))

        except ValidationError as e:
            return HttpResponseBadRequest(str(e.detail))

        return Response(status=status.HTTP_201_CREATED)

    def destroy(self, request, company_id, category_id):

        category_destroy_service = CategoryDestroyService(CategoryRepository())

        try:
            category_destroy_service.handle(company_id, category_id)

        except NotFound as e:
            raise Http404(str(e.detail))

        except ValidationError as e:
            return HttpResponseBadRequest(str(e.detail))

        return Response(status=status.HTTP_204_NO_CONTENT)

