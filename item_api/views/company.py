from rest_framework import viewsets
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView

from item_api.models import Company
from item_api.serializers.company import CompanyCreateSerializer


class CompanyListCreateAPIView(CreateAPIView, ListAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanyCreateSerializer

