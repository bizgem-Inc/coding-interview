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
]
