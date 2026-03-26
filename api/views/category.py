from rest_framework.viewsets import ModelViewSet

from api.models import Category
from api.serializers.category import CategorySerializer


class CategoryViewSet(ModelViewSet):
    """
    DRF の `ModelViewSet` に CRUD を任せつつ、要件の「`Category` の一覧/参照/作成/更新/削除」
    を満たすための最小構成にする。

    また、絞り込みが必要な場合を想定して `?company=<uuid>` で queryset を制限する。
    """

    serializer_class = CategorySerializer

    def get_queryset(self):
        qs = Category.objects.all()
        company_id = self.request.query_params.get("company")
        if company_id:
            qs = qs.filter(company_id=company_id)
        return qs
