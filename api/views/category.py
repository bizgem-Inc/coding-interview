from rest_framework import viewsets

from api.models import Category
from api.serializers.category import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def get_queryset(self):
        company_id = self.request.query_params.get("company_id")
        queryset = super().get_queryset()
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        return queryset.select_related("parent_category", "company")
