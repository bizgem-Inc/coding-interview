from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views.category import CategoryViewSet

router = DefaultRouter()
# ViewSetから一覧用・詳細用のURLを自動生成する。
router.register("categories", CategoryViewSet, basename="category")

urlpatterns = [path("", include(router.urls))]
