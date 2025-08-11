from django.urls import path
from api.views.category import CategoryListAPIView, CategoryDetailAPIView

urlpatterns = [
    path("categories/", CategoryListAPIView.as_view(), name="category-list"),
    path("categories/<uuid:pk>/", CategoryDetailAPIView.as_view(), name="category-detail"),
]
