from rest_framework import viewsets
from ..models.category import Category
from ..models.company import Company
from ..serializers.category import ApiCategorySerializer, ApiCompanySerializer

class ApiCategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = ApiCategorySerializer

class ApiCompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = ApiCompanySerializer
