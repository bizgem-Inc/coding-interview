from typing import Optional
import re

from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination

from item_api.exception.custom_exceptions import PutNotAllowedException


class BaseMasterMaintenanceViewSet(ModelViewSet):
    """
    マスタメンテナンス ViewSet の規定クラスです
    """

    def update(self, request, *args, **kwargs):
        """
        マスタメンテナンスの性質上、PUT でのリソースの置き換えは許可しません。POST で作成します。
        """
        if request.method == 'PUT':
            raise PutNotAllowedException()
        else:
            return super().update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 5  # 1ページあたりのアイテム数
    page_size_query_param = 'page_size'  # クエリパラメータでページサイズを指定可能
    max_page_size = 100  # ページサイズの上限


def extract_uuid(value: Optional[str]) -> Optional[str]:
    return None \
        if value is None else (
        re.search(r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b', value)[0]
    )
