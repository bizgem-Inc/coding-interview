# Author: abe
# Date: 2025-08-23
# Description: Category API views for coding interview

from rest_framework import viewsets, status
from rest_framework.response import Response
from api.models.category import Category
from api.serializers.category import CategoryListSerializer, CategoryCreateUpdateSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    カテゴリCRUD操作用ViewSet
    
    list: カテゴリ一覧取得
    retrieve: カテゴリ詳細取得
    create: カテゴリ作成
    update: カテゴリ更新
    partial_update: カテゴリ部分更新
    destroy: カテゴリ削除
    """
    queryset = Category.objects.all()
    
    def get_serializer_class(self):
        """アクションに応じて適切なシリアライザークラスを返す"""
        if self.action in ['list', 'retrieve']:
            return CategoryListSerializer
        return CategoryCreateUpdateSerializer
    
    def list(self, request, *args, **kwargs):
        """カテゴリ一覧取得（フィルタリング対応）"""
        queryset = self.get_queryset()
        
        # 企業によるフィルタリング
        company_id = request.query_params.get('company')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        # 親カテゴリによるフィルタリング
        parent_id = request.query_params.get('parent_category')
        if parent_id:
            if parent_id == 'null':
                queryset = queryset.filter(parent_category__isnull=True)
            else:
                queryset = queryset.filter(parent_category_id=parent_id)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """カテゴリ詳細取得"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def _get_response_with_full_details(self, instance, status_code=status.HTTP_200_OK):
        """詳細情報付きレスポンスを返すヘルパーメソッド"""
        #シリアライザーの出力を一定のフォーマットにする
        list_serializer = CategoryListSerializer(instance)
        return Response(list_serializer.data, status=status_code)
    
    def create(self, request, *args, **kwargs):
        """カテゴリ作成"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return self._get_response_with_full_details(serializer.instance, status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """カテゴリ更新"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return self._get_response_with_full_details(serializer.instance)
    
    def destroy(self, request, *args, **kwargs):
        """カテゴリ削除"""
        instance = self.get_object()
        
        # 子カテゴリがあるかチェック
        child_categories = Category.objects.filter(parent_category=instance)
        if child_categories.exists():
            return Response(
                {"error": "Cannot delete category with child categories. Please delete child categories first."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    

