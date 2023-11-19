from rest_framework import viewsets
from ..models.category import Category
from ..serializers.category import (
    ListSerializer,
    RetrieveSerializer,
    CreateSerializer,
    UpdateSerializer,
    DestroySerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    カテゴリのAPIのエントリポイント
    読み取り・作成・更新・削除を提供
    """

    queryset = Category.objects.all()

    serializer_map = {
        "create": CreateSerializer,
        "retrieve": RetrieveSerializer,
        "update": UpdateSerializer,
        "partial_update": UpdateSerializer,
        "destroy": DestroySerializer,
        "list": ListSerializer,
    }

    def get_serializer_class(self):
        """
        methodによってserializerを変える
        """
        return CategoryViewSet.serializer_map[self.action]
