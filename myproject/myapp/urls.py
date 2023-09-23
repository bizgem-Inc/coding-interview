from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.category import CategoryViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
