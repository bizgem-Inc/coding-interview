from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views.category import CategoryViewSet

router = DefaultRouter()

urlpatterns = [
    path("", include(router.urls)),
    path(
        "companies/<uuid:company_id>/categories/",
        CategoryViewSet.as_view({
            "get": "list"
        }),
    ),
    path(
        "companies/<uuid:company_id>/categories/<uuid:category_id>/",
        CategoryViewSet.as_view({
            "get": "retrieve",
            "delete": "destroy"
        }),
    ),
]
