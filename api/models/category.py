import uuid

from django.db import models

from .company import Company


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, related_name="+", on_delete=models.CASCADE, db_comment="企業ID")
    name = models.CharField(max_length=255, db_comment="カテゴリ名")
    parent_category = models.ForeignKey("self", blank=True, null=True, related_name="+", on_delete=models.SET_NULL, db_comment="親カテゴリID")
    created_at = models.DateTimeField(auto_now_add=True, editable=False, db_comment="作成日時")
    updated_at = models.DateTimeField(auto_now=True, editable=False, db_comment="更新日時")

    class Meta:
        db_table = "categories"
        db_table_comment = "カテゴリテーブル"
        verbose_name = "category"
        verbose_name_plural = "categories"
        constraints = [models.UniqueConstraint(fields=["company", "name"], name="unique_company_category_combination")]
        indexes = [models.Index(fields=["company", "name"])]
