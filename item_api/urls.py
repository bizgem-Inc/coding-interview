from django.urls import include, path
from rest_framework.routers import DefaultRouter

from item_api.views.company import CompanyListCreateAPIView

router = DefaultRouter()

urlpatterns = [
    path('companies',   CompanyListCreateAPIView.as_view())
]