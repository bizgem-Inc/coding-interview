from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views.category import CategoryView

router = DefaultRouter()
router.register('category', CategoryView)

urlpatterns = [
    # 備忘
    # ModelViewSetは以下のメソッドが利用可能。 アクセスしてきたurlとメソッドの種類で自動判別される。
    # list() retrieve() create() update() partial_update() destroy()
    path("", include(router.urls)),
    
    # 備忘
    # as_viewに渡す引数でCRUDを使うことができる。この辺が使えそう create(), retrieve(), update(), partial_update(), destroy() list() 
    # アドレスを変更したい場合は細かく分けることもできそう。
    # path("category_list/", CategoryView.as_view({'get':'list'})),
    # path("category_detail/<str:pk>/", CategoryView.as_view({'get':'retrieve'})),
    # path("category_create/", CategoryView.as_view({'get':'create'})),
    # path("category_delete/<str:pk>/", CategoryView.as_view({'get':'destroy'})),
]
