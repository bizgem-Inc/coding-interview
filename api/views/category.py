from rest_framework import viewsets

from api.models.category import Category
from api.serializers.category import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    CategoryモデルのCRUD操作を提供するViewSet
    
    - list: カテゴリ一覧の取得
    - retrieve: カテゴリ詳細の取得
    - create: カテゴリの作成
    - update: カテゴリの更新（全フィールド）
    - partial_update: カテゴリの部分更新
    - destroy: カテゴリの削除
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

