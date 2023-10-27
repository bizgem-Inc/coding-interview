from django.contrib import admin

from .models.category import Category
from .models.company import Company

admin.site.register(Category)
admin.site.register(Company)