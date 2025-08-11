from drf_yasg import openapi
from api.serializers.category import CategoryListSerializer, CategoryDetailSerializer


# Swaggerパラメータ定義
category_list_params = [
    openapi.Parameter(
        "company",
        openapi.IN_QUERY,
        description="会社IDでフィルタリング",
        type=openapi.TYPE_INTEGER,
        required=False,
    ),
    openapi.Parameter(
        "name",
        openapi.IN_QUERY,
        description="カテゴリ名で部分一致検索",
        type=openapi.TYPE_STRING,
        required=False,
    ),
    openapi.Parameter(
        "parent_category",
        openapi.IN_QUERY,
        description="親カテゴリIDでフィルタリング",
        type=openapi.TYPE_INTEGER,
        required=False,
    ),
    openapi.Parameter(
        "ordering",
        openapi.IN_QUERY,
        description="並び順（name, -name, created_at, -created_at, updated_at, -updated_at）",
        type=openapi.TYPE_STRING,
        required=False,
        default="name",
    ),
    openapi.Parameter(
        "page",
        openapi.IN_QUERY,
        description="ページ番号",
        type=openapi.TYPE_INTEGER,
        required=False,
    ),
    openapi.Parameter(
        "page_size",
        openapi.IN_QUERY,
        description="1ページあたりの件数",
        type=openapi.TYPE_INTEGER,
        required=False,
    ),
]


# レスポンス定義
category_list_response = openapi.Response(
    description="カテゴリ一覧",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "count": openapi.Schema(type=openapi.TYPE_INTEGER, description="総件数"),
            "next": openapi.Schema(type=openapi.TYPE_BOOLEAN, description="次ページの存在"),
            "previous": openapi.Schema(type=openapi.TYPE_BOOLEAN, description="前ページの存在"),
            "results": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER, description="カテゴリID"),
                        "name": openapi.Schema(type=openapi.TYPE_STRING, description="カテゴリ名"),
                        "updated_at": openapi.Schema(
                            type=openapi.FORMAT_DATETIME, description="更新日時"
                        ),
                        "created_at": openapi.Schema(
                            type=openapi.FORMAT_DATETIME, description="作成日時"
                        ),
                    },
                ),
                description="カテゴリデータのリスト",
            ),
        },
    ),
)

# 詳細レスポンス用のスキーマ
category_detail_response = CategoryDetailSerializer
