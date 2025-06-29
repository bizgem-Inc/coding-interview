import uuid
from django.db import models
from django.core.exceptions import ValidationError
from .company import Company


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, related_name="+", on_delete=models.CASCADE, db_comment="企業ID")
    name = models.CharField(max_length=255, db_comment="カテゴリ名")
    parent_category = models.ForeignKey("self", null=True, blank=True, related_name="+", on_delete=models.SET_NULL, db_comment="親カテゴリID")
    created_at = models.DateTimeField(auto_now_add=True, editable=False, db_comment="作成日時")
    updated_at = models.DateTimeField(auto_now=True, editable=False, db_comment="更新日時")

    class Meta:
        db_table = "categories"
        db_table_comment = "カテゴリテーブル"
        verbose_name = "category"
        verbose_name_plural = "categories"
        constraints = [models.UniqueConstraint(fields=["company", "name"], name="unique_company_category_combination")]
        indexes = [models.Index(fields=["company", "name"])]

    def clean(self):
        """
        - 親カテゴリとの関係性チェック
        - 循環参照のチェック
        - 同じ会社内での名前の重複チェック
        """
        if self.parent_category:
            if self.parent_category.company_id != self.company_id:
                raise ValidationError({
                    'parent_category': '親カテゴリは同じ会社のカテゴリのみ指定できます'
                })
            
            if self.has_circular_reference():
                raise ValidationError({
                    'parent_category': 'カテゴリの参照が循環しています'
                })

        # 同じ会社内での名前の重複チェック
        if self.name and self.company:
            existing = Category.objects.filter(company=self.company, name=self.name)
            if self.id:
                existing = existing.exclude(id=self.id)
            if existing.exists():
                raise ValidationError({
                    'name': '同じ会社内で同じ名前のカテゴリは作成できません'
                })

    def has_circular_reference(self):
        """
        循環参照をチェック
        - 自分自身を親に指定している
        - 親カテゴリを辿っていくと自分に戻ってくる
        """
        if not self.parent_category:
            return False

        visited = set()
        current = self.parent_category
        while current:
            if current.id in visited:
                return True
            if current.id == self.id:
                return True
            visited.add(current.id)
            current = current.parent_category
        return False

    def get_ancestors(self):
        """
        親カテゴリを全て取得（最上位から順）
        """
        ancestors = []
        current = self.parent_category
        while current:
            ancestors.insert(0, current)
            current = current.parent_category
        return ancestors

    def get_descendants(self):
        """
        子カテゴリを全て取得（再帰的に）
        """
        return Category.objects.filter(parent_category=self)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
