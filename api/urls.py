from django.urls import URLPattern, include, path
from rest_framework.routers import DefaultRouter

from api.views.category import CategoryViewSet

router: DefaultRouter = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")

urlpatterns: list[URLPattern] = [path("", include(router.urls))]