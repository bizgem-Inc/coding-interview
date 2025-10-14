from rest_framework import viewsets, status
from api.models.category import Category
from api.serializers.category import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):

    queryset = Category.objects.all().order_by("created_at")
    serializer_class = CategorySerializer
