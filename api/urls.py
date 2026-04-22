from django.urls import path
from api.views.category import CategoryView

urlpatterns = [
    # カテゴリ一覧の取得、および新規作成
    path(
        "companies/<str:company_id>/categories/",
        CategoryView.as_view(),
        name="categories"
    ),
    # 特定カテゴリの詳細取得、更新、および削除
    path(
        "companies/<str:company_id>/categories/<str:category_id>/",
        CategoryView.as_view(),
        name="category-detail"
    ),
]
