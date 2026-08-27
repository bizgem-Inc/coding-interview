from rest_framework import viewsets

from api.models import Category
from api.serializers.category import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """カテゴリの一覧取得・個別取得・作成・更新・削除を提供する。"""

    queryset = Category.objects.order_by("created_at")
    serializer_class = CategorySerializer
