from rest_framework.viewsets import ModelViewSet

from item_api.exception.custom_exceptions import PutNotAllowedException
from item_api.models import Company
from item_api.serializers.company import CompanySerializer
from item_api.views import CustomPageNumberPagination


class CompanyAPIView(ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    pagination_class = CustomPageNumberPagination

    def update(self, request, *args, **kwargs):
        """
        マスタメンテナンスの性質上、PUT でのリソースの置き換えは許可しません。POST で作成します。
        """
        if request.method == "PUT":
            raise PutNotAllowedException()
        else:
            return super().update(request, *args, **kwargs)
