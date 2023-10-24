import inject
from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = "api"

    def ready(self):
        from config.inject import default_config

        """
        DI設定
        アプリケーションにおいてどのDI設定を利用するか設定
        """
        inject.configure_once(default_config)
