from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (category,
                    company)

router = DefaultRouter()

router.register(r'categories', category.CategoryViewSet)
router.register(r'companies', company.CompanyViewSet)
urlpatterns = [path(r'', include(router.urls)),]
