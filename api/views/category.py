from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from ..models.category import Category
from ..serializers.category import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]  # 認証不要

    def get_queryset(self):
        return (
            Category.objects
            .select_related("company", "parent_category")
            .order_by("created_at")
        )
