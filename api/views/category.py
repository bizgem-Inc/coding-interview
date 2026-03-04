from rest_framework import viewsets

from api.models.category import Category
from api.serializers.category import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    Categoryモデルの CRUD API

    - GET    /api/categories/       : カテゴリ一覧取得
    - POST   /api/categories/       : カテゴリ作成
    - GET    /api/categories/{id}/  : カテゴリ詳細取得
    - PUT    /api/categories/{id}/  : カテゴリ更新
    - PATCH  /api/categories/{id}/  : カテゴリ部分更新
    - DELETE /api/categories/{id}/  : カテゴリ削除
    """

    queryset = Category.objects.select_related("company", "parent_category").all()
    serializer_class = CategorySerializer

