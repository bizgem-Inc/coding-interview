from rest_framework import viewsets
from ..models.category import Category
from ..serializers.category import ApiCategorySerializer

class ApiCategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = ApiCategorySerializer
