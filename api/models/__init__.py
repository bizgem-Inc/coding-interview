from .company import Company
from .category import Category

# ここにDBモデルを記載しないとdocker-compose exec app python manage.py makemigrationsしてもmigrations配下にマイグレーションファイルは作成されない
__all__ = ["Company", "Category"]
