from rest_framework import viewsets, filters
from rest_framework.filters import SearchFilter
from ..models.company import Company

class ApiCompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
  