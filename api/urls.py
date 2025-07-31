from django.urls import include, path

from .views.category import CategoryViewSet


list_create_view = CategoryViewSet.as_view({
    "get": "list",
    "post": "create",
})

detail_view = CategoryViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})

urlpatterns = [
    path("companies/<uuid:company_id>/categories/<int:pk>/", detail_view, name="category-detail"),
    path("companies/<uuid:company_id>/categories/", list_create_view, name="category-list-create"),
]
