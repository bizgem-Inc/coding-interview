from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter
from rest_framework import serializers, viewsets
from .models.category import Category
from .models.company import Company


class ApiCategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ('company', 'name', 'parent_category')

class ApiCompanySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Company
        fields = ('name')

class ApiCategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = ApiCategorySerializer

class ApiCompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = ApiCompanySerializer

router = DefaultRouter()
router.register(r'category', ApiCategoryViewSet)
router.register(r'company', ApiCompanyViewSet)

urlpatterns = [
    re_path(r'^', include(router.urls)),
    re_path(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]



