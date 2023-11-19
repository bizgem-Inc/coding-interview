from rest_framework import viewsets, mixins
from ..models.company import Company
from ..serializers.company import (
    CompanyListSerializer,
    CompanyCreateSerializer
)


class CompanyViewSet(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     viewsets.GenericViewSet):
    """
    企業のAPIのエントリポイントとなるクラス
    category作成のバリエーションを考慮し、作成と一覧表示を提供
    """
    queryset = Company.objects.all()
    serializer_class = CompanyListSerializer

    def get_serializer_class(self):
        """
        methodによってserializerを変える
        """
        if self.action == "list":
            return CompanyListSerializer
        return CompanyCreateSerializer
