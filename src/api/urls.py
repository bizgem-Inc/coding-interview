from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views.category import CategoryCreateAPIView, CategoryDetailAPIView, CategoryUpdateAPIView, CategoryDeleteAPIView, CategoryListAPIView

router = DefaultRouter()

urlpatterns = [
    path("category/create", CategoryCreateAPIView.as_view()),
    path("category/get/<uuid:id>", CategoryDetailAPIView.as_view()),
    path("category/list", CategoryListAPIView.as_view()),
    path("category/update", CategoryUpdateAPIView.as_view()),
    path("category/delete/<uuid:id>", CategoryDeleteAPIView.as_view()),
]
