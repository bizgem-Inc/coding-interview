from typing import Optional
import re

from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 5  # 1ページあたりのアイテム数
    page_size_query_param = 'page_size'  # クエリパラメータでページサイズを指定可能
    max_page_size = 100  # ページサイズの上限


def extract_uuid(value: Optional[str]) -> Optional[str]:
    return None \
        if value is None else (
        re.search(r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b', value)[0]
    )
