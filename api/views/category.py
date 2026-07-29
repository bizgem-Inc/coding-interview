from rest_framework import viewsets

from ..models import Category
from ..serializers import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """Category の一覧取得・詳細取得・作成・更新・削除を提供する ViewSet。"""

    queryset = Category.objects.select_related("company", "parent_category").order_by("created_at", "id")
    serializer_class = CategorySerializer
