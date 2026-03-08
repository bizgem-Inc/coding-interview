from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from api.repository import CategoryRepository
from api.serializers.category import CategorySerializer
from api.service import CategoryListService, CategoryRetrieveService, CategoryDestroyService


class CategoryViewSet(ViewSet):

    def list(self, request, company_id):

        categories = CategoryListService(CategoryRepository()).handle(company_id)

        return Response(CategorySerializer(categories, many=True).data)

    def retrieve(self, request, company_id, category_id):

        category = CategoryRetrieveService(CategoryRepository()).handle(company_id, category_id)

        if category is None:
            raise Http404("Category not found")

        return Response(CategorySerializer(category, many=False).data)

    def destroy(self, request, company_id, category_id):

        category_destroy_service = CategoryDestroyService(CategoryRepository())

        try:
            category_destroy_service.handle(company_id, category_id)
        except NotFound as e:
            raise Http404(str(e.detail))

        return Response(status=status.HTTP_204_NO_CONTENT)

