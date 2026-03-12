from django.db.models import QuerySet
from rest_framework import viewsets

from api.models.category import Category
from api.serializers.category import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    カテゴリのCRUD操作を行うViewSet
    """

    queryset: QuerySet[Category] = Category.objects.all()
    serializer_class: type[CategorySerializer] = CategorySerializer