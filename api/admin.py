from django.contrib import admin
from api.models import Category, Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("name",)
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "company",
        "parent_category",
        "path",
        "created_at",
        "updated_at",
    )
    list_filter = ("company", "created_at", "updated_at")
    search_fields = ("name", "company__name")
    readonly_fields = ("id", "path", "created_at", "updated_at")
    raw_id_fields = ("parent_category",)

    fieldsets = (
        (None, {"fields": ("name", "company", "parent_category")}),
        (
            "システム情報",
            {
                "fields": ("id", "path", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )
