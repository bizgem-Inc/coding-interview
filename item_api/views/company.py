
from item_api.models import Company
from item_api.serializers.company import CompanySerializer
from item_api.views import BaseMasterMaintenanceViewSet, CustomPageNumberPagination


class CompanyViewSet(BaseMasterMaintenanceViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    pagination_class = CustomPageNumberPagination


