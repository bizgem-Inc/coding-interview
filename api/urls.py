from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views.category import CategoryViewSet
from api.views.company import CompanyViewSet

router = DefaultRouter()
router.register(r"categories", CategoryViewSet)
router.register(r"companies", CompanyViewSet)

urlpatterns = [path("", include(router.urls))]