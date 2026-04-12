from uuid import UUID

from django.db import models as db_models
from django.db.models import Prefetch
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from api.models.company import Company
from api.models.category import Category
from api.serializers.category import (
    CategoryListSerializer,
    CategoryDetailSerializer,
    CategoryWriteSerializer,
)

class CategoryPagination(PageNumberPagination):
    page_size = 20  # 1ページあたりの件数
    page_size_query_param = 'page_size'
    max_page_size = 100


class CategoryViewSet(viewsets.ModelViewSet):
    """
    カテゴリ操作を管理するViewSet。
    管理画面でのドリルダウンUIを支援するため、階層別の取得と整合性チェックを重視しています。
    """
    http_method_names = ["get", "post", "patch", "delete"]
    pagination_class = CategoryPagination

    def get_company(self):
        # TODO: 認証実装後に request.user.company_id で取得
        # NOTE:
        # 認証ロジックは未実装のため、`get_company()` は暫定実装としています。本番では `request.user.company_id` から取得する想定で、現時点ではテスト・手動確認のための便宜実装です。
        return Company.objects.order_by('created_at').first()

    def get_queryset(self):
        """
        企業スコープでのフィルタリングと、ドリルダウン用の階層絞り込みを行います。
        """
        company = self.get_company()
        queryset = Category.objects.filter(company=company)

        # destroy は軽量クエリを返却
        if self.action == 'destroy':
            return queryset

        if self.action == "retrieve":
            return self._apply_annotations(queryset, with_children=True)

        # list アクション以外は階層フィルタをかけずに返却
        if self.action != 'list':
            return self._apply_annotations(queryset, with_children=False)

        # list 時のドリルダウンフィルタ
        # parent_category_id による 1 階層ずつの絞り込み（ドリルダウン対応）
        # ?parent_category_id="", 指定なしの場合はルートカテゴリを取得
        parent_id = self.request.query_params.get('parent_category_id')

        if parent_id:
            try:
                # UUIDとして正しい形式かチェック
                UUID(str(parent_id))
            except ValueError:
                # 形式が正しくない場合は 400 エラーを投げる
                raise ValidationError({
                    "parent_category_id": ["有効なカテゴリIDを指定してください。"]
                })

            queryset = queryset.filter(parent_category_id=parent_id)
        else:
            queryset = queryset.filter(parent_category__isnull=True)

        return self._apply_annotations(queryset, with_children=False)

    def _apply_annotations(self, queryset, with_children=False):
        queryset = (
            queryset
            .annotate(children_count=db_models.Count("children"))
            .select_related("parent_category")
            .order_by("created_at")
        )
        if with_children:
            queryset = queryset.prefetch_related(
                Prefetch("children", queryset=Category.objects.order_by("name", "created_at"))
            )
        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CategoryDetailSerializer
        if self.action in ["create", "partial_update"]:
            return CategoryWriteSerializer
        return CategoryListSerializer

    def get_serializer_context(self):
        """
        Serializer内での企業スコープチェック等のために company をコンテキストに含めます。
        """
        context = super().get_serializer_context()
        context["company"] = self.get_company()
        return context

    def destroy(self, request, *args, **kwargs):
        """
        物理削除を実行します。
        データの不整合を防ぐため、子カテゴリが存在する場合は削除をブロックします。
        """
        instance = self.get_object()

        # 物理削除前の整合性バリデーション
        # 直下の子カテゴリが存在する場合、ツリー構造の破壊を防ぐため削除を禁止
        if instance.children.exists():
            return Response(
                {"detail": "子カテゴリが存在するため削除できません。子カテゴリを先に削除または移動させてください。"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # TODO: 将来的に 販売商品 や 受注商品 モデルが実装された際に
        # それらに使用されているカテゴリの削除を制限するチェックを以下に追加します

        # 物理削除を実行
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
