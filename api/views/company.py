from rest_framework import viewsets
from api.models.company import Company
from api.serializers.company import CompanySerializer


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
