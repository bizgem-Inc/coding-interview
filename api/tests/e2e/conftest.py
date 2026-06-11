import pytest
import httpx

from api.repositories.django.orm_models.category import CategoryModel
from api.repositories.django.orm_models.company import CompanyModel

# E2Eテスト全体でDBアクセスを有効にする
pytestmark = pytest.mark.django_db


@pytest.fixture
def company(db):  # type: ignore[no-untyped-def]
    """E2Eテスト用のCompanyを事前作成する。"""
    company, _ = CompanyModel.objects.get_or_create(
        name="E2E Test Corp",
    )
    return company


@pytest.fixture
def client(live_server):  # type: ignore[no-untyped-def]
    """live_serverに接続するhttpxクライアント。"""
    return httpx.Client(base_url=live_server.url)


@pytest.fixture(autouse=True)
def _cleanup_categories(db, company):  # type: ignore[no-untyped-def]
    """テスト後にCategoryをクリーンアップする。"""
    yield
    CategoryModel.objects.filter(company=company).delete()
