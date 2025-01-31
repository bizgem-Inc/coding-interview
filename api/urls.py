from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api import views

router = DefaultRouter()

router.register('category',views.CategoryViewSet, basename='category')
router.register('company',views.CompanyViewSet, basename='company')

urlpatterns = [path("", include(router.urls))]
