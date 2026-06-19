from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import QuerySet

from api.models.category import Category

if TYPE_CHECKING:
    from api.serializers.category import CategorySerializer


class CategoryService:
    # ViewSetからDB操作を直接行わないための薄いサービス層。
    # 将来、作成・更新時の追加処理が増えてもViewSetを太らせずに済む。

    @staticmethod
    def get_queryset() -> QuerySet[Category]:
        # 一覧と詳細で使う取得条件はここに寄せて、ViewSet側を薄く保つ。
        return Category.objects.select_related("company", "parent_category").order_by("name")

    @staticmethod
    def create(serializer: CategorySerializer) -> Category:
        # serializer側のvalidated_dataをそのまま使って保存する。
        return serializer.save()

    @staticmethod
    def update(serializer: CategorySerializer) -> Category:
        # 更新時も保存の入口をservice層に揃える。
        return serializer.save()

    @staticmethod
    def delete(category: Category) -> None:
        # 削除対象はViewSetが取得済みのインスタンスを使う。
        category.delete()
