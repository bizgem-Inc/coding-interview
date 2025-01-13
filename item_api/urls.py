from django.urls import include, path
from rest_framework.routers import DefaultRouter

from item_api.views.category import CategoryAPIView
from item_api.views.company import CompanyAPIView

router = DefaultRouter(trailing_slash=False)
router.register('companies', CompanyAPIView, basename='company')
router.register('categories', CategoryAPIView, basename='category')
urlpatterns = [
    path('',   include(router.urls)),
]