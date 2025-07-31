from rest_framework.viewsets import ModelViewSet

from ..models.category import Category
from ..serializers.category import CategoryModelSerializer


class CategoryViewSet(ModelViewSet):
    serializer_class = CategoryModelSerializer
    queryset = Category.objects.all()
