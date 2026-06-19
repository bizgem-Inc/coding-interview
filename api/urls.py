# APIルーティングを定義するためのDjango/DRF標準部品を利用する。
from django.urls import include, path
from rest_framework.routers import DefaultRouter

# CategoryのCRUD APIを提供するViewSetを読み込む。
from api.views.category import CategoryViewSet

# DefaultRouterを使うことで、list/retrieve/create/update/destroyのURLを自動生成する。
router = DefaultRouter()

# /api/categories/ 配下にCategory CRUDエンドポイントを登録する。
router.register("categories", CategoryViewSet, basename="category")

# config.urlsからincludeされるAPI URL一覧。
urlpatterns = [path("", include(router.urls))]
