from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views.category import CategoryAPIView

router = DefaultRouter()

urlpatterns = [
    path("categories/", CategoryAPIView.as_view()),
    path("categories/<uuid:pk>/", CategoryAPIView.as_view()),
]
