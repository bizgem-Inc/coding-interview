from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views.category import CategoryViewSet

router = DefaultRouter()
router.register(prefix='categories', viewset=CategoryViewSet, basename='category')

urlpatterns = [path("", include(router.urls))]
