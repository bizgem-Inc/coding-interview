from rest_framework.viewsets import ModelViewSet

from api.models import Category
from api.serializers import CategorySerializer


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
