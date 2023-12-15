from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views.category import CategoryViewSet

app_name = 'api'

router = DefaultRouter()
router.register('categories', CategoryViewSet)

urlpatterns = [path("", include(router.urls))]
