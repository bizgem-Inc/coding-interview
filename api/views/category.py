from rest_framework.viewsets import ModelViewSet

from api.models.category import Category
from api.serializers.category import CategorySerializer


class CategoryViewSet(ModelViewSet):
    """Provide CRUD actions for categories."""

    authentication_classes = []
    permission_classes = []
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
