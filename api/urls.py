from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter
from .views.category import ApiCategoryViewSet, ApiCompanyViewSet

router = DefaultRouter()
router.register(r'category', ApiCategoryViewSet)
router.register(r'company', ApiCompanyViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]



