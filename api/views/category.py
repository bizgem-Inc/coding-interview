from rest_framework import viewsets

from api.models.category import Category
from api.serializers.category import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    CategoryモデルのCRUDを提供するビューセット
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
