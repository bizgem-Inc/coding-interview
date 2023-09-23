from django.contrib import admin

# Register your models here.

# モデルをインポート
from .models.category import Category
from .models.category import Company

# 管理ツールに登録
admin.site.register(Category)
admin.site.register(Company)
