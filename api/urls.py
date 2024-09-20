from rest_framework.routers import DefaultRouter

from .views.category import CategoryViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
