from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter
from .views.category import ApiCategoryViewSet

router = DefaultRouter()
router.register(r'category', ApiCategoryViewSet)

urlpatterns = [path('', include(router.urls))]