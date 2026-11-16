from rest_framework import viewsets

from api.models import Category
from api.serializers.category import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """カテゴリの CRUD API。

    - GET    /api/categories/       一覧(作成日時の昇順)
    - POST   /api/categories/       作成
    - GET    /api/categories/{id}/  取得
    - PUT    /api/categories/{id}/  更新
    - PATCH  /api/categories/{id}/  部分更新
    - DELETE /api/categories/{id}/  削除(子カテゴリの parent_category は null になる)
    """

    # UUID 主キーでは順序が定まらないため、作成日時順で返す
    queryset = Category.objects.order_by("created_at", "id")
    serializer_class = CategorySerializer
