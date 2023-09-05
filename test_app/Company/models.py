import uuid
from django.db import models

class Company(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, db_comment='企業ID')
    name = models.CharField(max_length=255, db_comment='企業名')
    created_at = models.DateTimeField(auto_now_add=True, db_comment='作成日時')
    updated_at = models.DateTimeField(auto_now=True, db_comment='更新日時')

    class Meta:
        db_table = 'companies'
        db_table_comment = '企業テーブル'
        verbose_name = 'company'
        verbose_name_plural = 'companies'
