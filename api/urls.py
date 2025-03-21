from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views.category import CategoryViewSet

router = DefaultRouter()

urlpatterns = [
    path("", include(router.urls)),
    path(
        "categories/",
        CategoryViewSet.as_view({"get": "list", "post": "create"}),
        name="categories",
    ),
    path(
        "categories/<uuid:category_id>/",
        CategoryViewSet.as_view(
            {"get": "retrieve", "patch": "update", "delete": "destroy"}
        ),
        name="category-detail",
    ),
]
