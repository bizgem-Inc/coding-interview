from rest_framework import viewsets
from ..models.category import Category
from ..serializers.category import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.select_related('company').select_related('parent_category').all()
    serializer_class = CategorySerializer
