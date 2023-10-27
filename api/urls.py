<<<<<<< HEAD
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = [path("", include(router.urls))]
=======
from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter
from .views.category import ApiCategoryViewSet
from .views.company import ApiCompanyViewSet

router = DefaultRouter()
router.register(r'category', ApiCategoryViewSet)

urlpatterns = [path('', include(router.urls))]
>>>>>>> upstream/master
