from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views.category import (
    CategoryListCreateAPIView,
    CategoryRetrieveUpdateDestroyAPIView,
)


router = DefaultRouter()

urlpatterns = [
    path("", include(router.urls)),
                 # Category API の URL を追加
    path("categories/", CategoryListCreateAPIView.as_view(), name="category-list-create"),
    path("categories/<uuid:pk>/", CategoryRetrieveUpdateDestroyAPIView.as_view(), name="category-detail"),
               ]
