from rest_framework import viewsets, status
from rest_framework.response import Response
from ..models.category import Category
from ..serializers.category import CategorySerializer

class CategoryViewSet(viewsets.ModelViewSet):
    """
    CategoryモデルのCRUD操作を提供するViewSet
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
