# Djangoのモデル検出用import窓口。業務ロジックは置かない。
from api.repositories.django.orm_models.category import CategoryModel  # noqa: F401
from api.repositories.django.orm_models.company import CompanyModel  # noqa: F401
