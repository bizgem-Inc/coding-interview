from django.urls import path, include
from rest_framework.routers import DefaultRouter
from Company.views import CompanyViewSet

router = DefaultRouter()
router.register(r'companies', CompanyViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
