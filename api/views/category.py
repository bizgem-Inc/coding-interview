from rest_framework.viewsets import ModelViewSet

from ..models.category import Category
from ..serializers.category import CategoryModelSerializer


class CategoryViewSet(ModelViewSet):
    serializer_class = CategoryModelSerializer

    def get_queryset(self):
        return Category.objects.filter(company_id=self._company_id)

    def perform_create(self, serializer):
        serializer.save(company_id=self._company_id)

    @property
    def _company_id(self):
        return self.kwargs["company_id"]