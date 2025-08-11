import django
import os
import pytest

# Django settings moduleを設定
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Djangoのセットアップ
django.setup()

# pytest-djangoの設定
pytest_plugins = ["pytest_django"]


@pytest.fixture(scope="session", autouse=True)
def setup_staticfiles_directory():
    """テスト用の静的ファイルディレクトリを作成"""
    staticfiles_dir = "/app/staticfiles/"
    if not os.path.exists(staticfiles_dir):
        os.makedirs(staticfiles_dir, exist_ok=True)
