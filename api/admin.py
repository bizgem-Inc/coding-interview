from django.contrib import admin

from api.models import (
    category,
    company
)


@admin.register(category.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = (
        "id",
        'company_name',
        'name',
        'parent_category_name',
        'created_at',
        'updated_at')
    list_filter = ('name',)
    ordering = ('id', 'name',)
    search_fields = ('company_name', 'name',)

    def company_name(self, obj):
        """
        企業名
        """
        return obj.company.name
    company_name.short_description = "企業名"

    def parent_category_name(self, obj):
        """
        親カテゴリ名
        無ければ空文字
        """
        return obj.parent_category.name if obj.parent_category else ""
    parent_category_name.short_description = "親カテゴリ名"


@admin.register(company.Company)
class CompanyAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ('id',
                    'name',
                    'created_at',
                    'updated_at')
    ordering = ('name',)
    search_fields = ('name',)
