from rest_framework.viewsets import ModelViewSet

from api.models.category import Category
from api.serializers.category import CategorySerializer


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all().order_by("created_at")
    serializer_class = CategorySerializer
