# api/views/category.py
from rest_framework import viewsets

from api.models import Category
from api.serializers.category import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    Category の CRUD を提供する ViewSet
    認証は不要という前提
    """

    queryset = Category.objects.all().order_by("created_at")
    serializer_class = CategorySerializer
