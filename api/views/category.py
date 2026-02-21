from rest_framework import viewsets
from ..models.category import Category
from ..serializers.category import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    カテゴリのCRUD操作を提供するViewSet

    list:           カテゴリ一覧を取得
    create:         新しいカテゴリを作成
    retrieve:       特定のカテゴリを取得
    update:         カテゴリを更新
    partial_update: カテゴリを部分更新
    destroy:        カテゴリを削除（子カテゴリのparent_categoryはnullになる）
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
