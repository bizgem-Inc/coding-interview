from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = [
    path('companies', include('rest_framework.urls'))
]