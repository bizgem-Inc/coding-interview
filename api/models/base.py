from django.db import models
from django.core.validators import RegexValidator
from django.db.models.fields import TextField
from django import forms
from django.forms.widgets import TextInput

# メンテナンスが停滞しているため、必要なフィールドだけを引用して実装
# ref: https://github.com/mariocesar/django-ltree/blob/master/django_ltree/fields.py

ltree_path_validator = RegexValidator(
    r"^[a-zA-Z0-9_-]+(?:\.[a-zA-Z0-9_-]+)*$",
    "パスは英数字、アンダースコア、ハイフンで構成され、ドットで区切られる必要があります。",
    "invalid",
)


class LtreeFormField(forms.CharField):
    """Ltreeフィールド用のFormフィールド"""

    default_validators = [ltree_path_validator]


class LtreeField(TextField):
    """
    PostgreSQLのltree型を扱うためのカスタムフィールド

    ltree拡張機能を使用してMaterialized Pathパターンを実装します。
    """

    default_validators = [ltree_path_validator]
    description = "Materialized Path using PostgreSQL ltree"

    def __init__(self, *args, **kwargs):
        # ltreeフィールドは通常編集不可にする
        kwargs.setdefault("editable", False)
        super().__init__(*args, **kwargs)

    def db_type(self, connection):
        """PostgreSQLのltree型を使用"""
        return "ltree"

    def formfield(self, **kwargs):
        """管理画面などで使用するフォームフィールドを定義"""
        defaults = {
            "form_class": LtreeFormField,
            "widget": TextInput(attrs={"class": "vTextField"}),
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)

    def from_db_value(self, value, expression, connection):
        """データベースから取得した値をPythonオブジェクトに変換"""
        return value

    def get_prep_value(self, value):
        """Pythonオブジェクトをデータベースに保存する形式に変換"""
        if value is None:
            return None
        # 文字列として保存
        return str(value)

    def to_python(self, value):
        """任意の値をPythonの文字列に変換"""
        if value is None or value == "":
            return None
        return str(value)

    def get_db_prep_value(self, value, connection, prepared=False):
        """データベースクエリで使用する値に変換"""
        if value is None:
            return None
        return str(value)


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False, db_comment="作成日時")
    updated_at = models.DateTimeField(auto_now=True, editable=False, db_comment="更新日時")

    class Meta:
        abstract = True
        ordering = ["-created_at"]
