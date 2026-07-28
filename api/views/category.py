from rest_framework.viewsets import ModelViewSet

from api.models import Category
from api.serializers.category import CategorySerializer


class CategoryViewSet(ModelViewSet):
    """Categoryの一覧・詳細・作成・更新・削除APIを提供する。"""

    # 一覧の返却順が実行ごとに変わらないよう、並び順を固定する。
    queryset = Category.objects.all().order_by("created_at", "id")
    serializer_class = CategorySerializer
    # UUID形式でないIDはDB検索を行わず、URL不一致として404にする。
    lookup_value_regex = (
        r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
    )
