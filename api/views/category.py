from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet

from api.models import Category
from api.serializers.category import CategorySerializer


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.select_related("company", "parent_category").order_by("created_at", "id")
    serializer_class = CategorySerializer
    permission_classes = (AllowAny,)
