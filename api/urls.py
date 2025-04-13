from django.urls import path, include
from rest_framework import routers
from api.views.category import CategoryViewSet

router = routers.DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('api/', include(router.urls)),
]
