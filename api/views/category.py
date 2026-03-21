from rest_framework import viewsets

from api.models import Category
from api.serializers.category import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """Category の CRUD API"""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
