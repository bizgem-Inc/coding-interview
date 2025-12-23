from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
from .views.category import CategoryViewSet

router.register(r"categories", CategoryViewSet, basename="category")

urlpatterns = [path("", include(router.urls))]
