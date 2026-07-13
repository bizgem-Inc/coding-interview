from rest_framework import viewsets

from api.models.category import Category
from api.serializers.category import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.select_related("company", "parent_category").all()
    serializer_class = CategorySerializer
