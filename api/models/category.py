import uuid

from django.core.exceptions import ValidationError
from django.db import models

from .company import Company


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, related_name="+", on_delete=models.CASCADE, db_comment="企業ID")
    name = models.CharField(max_length=255, db_comment="カテゴリ名")
    parent_category = models.ForeignKey("self", null=True, blank=True, related_name="+", on_delete=models.SET_NULL, db_comment="親カテゴリID")
    created_at = models.DateTimeField(auto_now_add=True, editable=False, db_comment="作成日時")
    updated_at = models.DateTimeField(auto_now=True, editable=False, db_comment="更新日時")

    def clean(self):
        super().clean()
        if self.parent_category is None:
            return

        if self.parent_category == self:
            raise ValidationError(
                {"parent_category": "A category cannot be its own parent."}
            )

        if self.parent_category.company != self.company:
            raise ValidationError(
                {"parent_category": "Parent category must belong to the same company."}
            )

        # TODO: 利用例に応じて最大深度の制限を検討する
        ancestor = self.parent_category
        while ancestor is not None:
            if ancestor == self:
                raise ValidationError(
                    {"parent_category": "Circular reference detected."}
                )
            ancestor = ancestor.parent_category

    class Meta:
        db_table = "categories"
        db_table_comment = "カテゴリテーブル"
        verbose_name = "category"
        verbose_name_plural = "categories"
        constraints = [models.UniqueConstraint(fields=["company", "name"], name="unique_company_category_combination")]
        indexes = [models.Index(fields=["company", "name"])]
