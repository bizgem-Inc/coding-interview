from django.urls import include, path
from rest_framework.routers import DefaultRouter

from item_api.views.company import CompanyViewSet

router = DefaultRouter(trailing_slash=False)
router.register('companies', CompanyViewSet, basename='company')
urlpatterns = [
    path('',   include(router.urls)),
]