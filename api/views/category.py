from rest_framework import viewsets

from api.models import Category
from api.serializers import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer

    def get_queryset(self):
        queryset = Category.objects.order_by("created_at")
        # 一覧はテナント（企業）単位で参照するのが通常のため、company で絞り込めるようにする
        company_id = self.request.query_params.get("company")
        if company_id is not None:
            queryset = queryset.filter(company_id=company_id)
        return queryset
