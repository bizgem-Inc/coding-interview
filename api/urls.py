from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = [path("", include(router.urls))]
from .views.category import category_list, category_detail

urlpatterns += [
    path('categories/', category_list, name='category-list'),
    path('categories/<uuid:pk>/', category_detail, name='category-detail'),
]
