from rest_framework import viewsets

from api.models import Category
from api.serializers.category import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """カテゴリの読み取り・作成・更新・削除を提供するViewSet。"""

    # created_atだけでは同時刻のレコードで順序が定まらないため、idを第2キーにする。
    queryset = Category.objects.all().order_by("created_at", "id")
    serializer_class = CategorySerializer
