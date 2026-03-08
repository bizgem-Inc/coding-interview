from django.http import Http404
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from api.repository import CategoryRepository
from api.serializers.category import CategorySerializer
from api.service import CategoryListService, CategoryRetrieveService


class CategoryViewSet(ViewSet):

    def list(self, request, company_id):

        categories = CategoryListService(CategoryRepository()).handle(company_id)

        return Response(CategorySerializer(categories, many=True).data)

    def retrieve(self, request, company_id, category_id):

        category = CategoryRetrieveService(CategoryRepository()).handle(company_id, category_id)

        if category is None:
            raise Http404("Category not found")

        return Response(CategorySerializer(category, many=False).data)

