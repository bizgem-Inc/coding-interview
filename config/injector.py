from injector import Module, provider, Injector, singleton
from api.use_cases import CategoryRepository


class AppModule(Module):
    """アプリケーション全体のDI設定"""

    @singleton
    @provider
    def provide_category_repository(self) -> CategoryRepository:
        return CategoryRepository()


def create_injector() -> Injector:
    """Injectorインスタンスを作成"""
    return Injector([AppModule()])
