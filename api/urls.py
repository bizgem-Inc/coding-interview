from django.urls import path
from api.views.category import CategoryView
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def api_root(request):
    return Response({
        "message": "Welcome to Category API",
        "instructions": "Please access the URL using a valid company_id.",
        "example_url": "/api/companies/00000000-0000-0000-0000-000000000000/categories/"
    })

urlpatterns = [
    # APIルートの案内
    path("", api_root),
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
