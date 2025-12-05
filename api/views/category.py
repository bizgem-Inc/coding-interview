from rest_framework import generics
from api.models.category import Category
from api.serializers.category import CategorySerializer


class CategoryListCreateAPIView(generics.ListCreateAPIView):
    """
    GET  /categories/  → 一覧取得
    POST /categories/  → 作成
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /categories/<id>/ → 1件取得
    PUT    /categories/<id>/ → 全更新
    PATCH  /categories/<id>/ → 部分更新
    DELETE /categories/<id>/ → 削除
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
