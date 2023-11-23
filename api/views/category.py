from rest_framework import viewsets
from api.models.category import Category
from api.serializers.category import CategorySerializer

class CategoryView(viewsets.ModelViewSet):
    '''
    ModelViewSetは以下のメソッドが利用可能。
    アクセスしてきたurlとメソッドの種類で自動判別される。
    list() retrieve() create() update() partial_update() destroy()
    '''
    queryset = Category.objects.all()
    serializer_class = CategorySerializer