from __future__ import annotations

from django.db.models import QuerySet
from rest_framework import viewsets

from api.models.category import Category
from api.serializers.category import CategorySerializer
from api.services.category import CategoryService


class CategoryViewSet(viewsets.ModelViewSet):
    # HTTPリクエストの受け口に集中し、実処理はserializer/serviceへ委譲する。
    serializer_class = CategorySerializer

    def get_queryset(self) -> QuerySet[Category]:
        # 取得条件はservice層に集約する。
        return CategoryService.get_queryset()

    def perform_create(self, serializer: CategorySerializer) -> None:
        # DRFのバリデーション通過後、作成処理だけservice層へ渡す。
        CategoryService.create(serializer)

    def perform_update(self, serializer: CategorySerializer) -> None:
        # 更新処理も作成と同じ入口に揃える。
        CategoryService.update(serializer)

    def perform_destroy(self, instance: Category) -> None:
        # 削除処理もservice層へ寄せる。
        CategoryService.delete(instance)
