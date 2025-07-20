from django.db import IntegrityError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters
from rest_framework.response import Response

from api.models.category import Category
from api.serializers.category import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.select_related('company', 'parent_category')
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['company', 'parent_category']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def handle_exception(self, exc):
        if isinstance(exc, IntegrityError):
            if 'unique_company_category_combination' in str(exc):
                return Response(
                    {"error": "同じ企業内に同じ名前のカテゴリが既に存在します"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return super().handle_exception(exc)