import uuid

from django.db import models
from .base import BaseModel


class Company(BaseModel):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, db_comment="企業ID")
    name = models.CharField(max_length=255, db_comment="企業名")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "companies"
        db_table_comment = "企業テーブル"
        verbose_name = "company"
        verbose_name_plural = "companies"
