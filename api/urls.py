from django.urls import include, path
from rest_framework.routers import DefaultRouter
# from . import views
from api.views.category import CategoryViewSet
from api.views.company import CompanyViewSet

router = DefaultRouter()
router.register(r'category', CategoryViewSet)
router.register(r'company', CompanyViewSet)

urlpatterns = [path("", include(router.urls))]
