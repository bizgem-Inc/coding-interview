# Django起動時に両モデルがapiアプリへ登録されるよう、明示的に読み込む。
from .company import Company
from .category import Category

__all__ = ["Company", "Category"]
