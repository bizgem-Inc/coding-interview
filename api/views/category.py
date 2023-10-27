import django_filters.rest_framework
from rest_framework import viewsets, filters
from rest_framework.filters import SearchFilter
from ..models.category import Category
from ..serializers.category import ApiCategorySerializer

class NameFilter(filters.BaseFilterBackend):
  def filter_queryset(self, request, queryset, view):
    if request.query_params.get('name'):
      return queryset.filter(name=request.query_params.get('name'))
    elif request.query_params.get('company'):
      return queryset.filter(company__name=request.query_params.get('company'))
    elif request.query_params.get('parent_category'):
      return queryset.filter(parent_category__name=request.query_params.get('parent_category'))
    return queryset

class ApiCategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = ApiCategorySerializer
    filter_backends = [ NameFilter ]
    search_fields = ['company__name', 'name', 'parent_category__name']
  