from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from rest_framework import viewsets

from api.models.category import Category
from api.serializers.category import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """CategoryのCRUD API"""

    queryset = Category.objects.select_related('company', 'parent_category').all()
    serializer_class = CategorySerializer

    @extend_schema(
        summary="カテゴリ一覧取得",
        description="すべてのカテゴリを取得します。",
        responses={
            200: CategorySerializer(many=True),
            500: OpenApiResponse(
                description="サーバー内部エラー",
                examples=[
                    OpenApiExample(
                        "サーバーエラー",
                        value={"detail": "サーバー内部エラーが発生しました。"},
                        response_only=True,
                    ),
                ],
            ),
        },
    )
    def list(self, request, *args, **kwargs):
        """
        メソッド名：カテゴリ一覧取得\n
        メソッド: GET\n
        PATH: /api/categories/
        """
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="カテゴリ取得",
        description="IDを指定してカテゴリを取得します。",
        responses={
            200: CategorySerializer,
            404: OpenApiResponse(
                description="カテゴリが見つかりません",
                examples=[
                    OpenApiExample(
                        "カテゴリが存在しない",
                        value={"detail": "見つかりませんでした。"},
                        response_only=True,
                    ),
                ],
            ),
            500: OpenApiResponse(
                description="サーバー内部エラー",
                examples=[
                    OpenApiExample(
                        "サーバーエラー",
                        value={"detail": "サーバー内部エラーが発生しました。"},
                        response_only=True,
                    ),
                ],
            ),
        },
    )
    def retrieve(self, request, *args, **kwargs):
        """
        メソッド名：カテゴリ取得(ID指定)\n
        メソッド: GET\n
        PATH: /api/categories/{id}/
        """
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="カテゴリ作成",
        description="新しいカテゴリを作成します。",
        responses={
            201: CategorySerializer,
            400: OpenApiResponse(
                description="バリデーションエラー",
                examples=[
                    OpenApiExample(
                        "カテゴリ名が空",
                        value={"name": ["カテゴリ名は必須です。"]},
                        response_only=True,
                    ),
                    OpenApiExample(
                        "カテゴリ名が長すぎる",
                        value={"name": ["カテゴリ名は255文字以内で入力してください。"]},
                        response_only=True,
                    ),
                    OpenApiExample(
                        "同名カテゴリが既に存在",
                        value={
                            "name": ["この企業には既に同じ名前のカテゴリが存在します。"]
                        },
                        response_only=True,
                    ),
                    OpenApiExample(
                        "親カテゴリが異なる企業",
                        value={
                            "parent_category": [
                                "親カテゴリは同じ企業に属している必要があります。"
                            ]
                        },
                        response_only=True,
                    ),
                    OpenApiExample(
                        "親カテゴリが存在しない",
                        value={
                            "parent_category": ["指定された親カテゴリが存在しません。"]
                        },
                        response_only=True,
                    ),
                ],
            ),
            500: OpenApiResponse(
                description="サーバー内部エラー",
                examples=[
                    OpenApiExample(
                        "サーバーエラー",
                        value={"detail": "サーバー内部エラーが発生しました。"},
                        response_only=True,
                    ),
                ],
            ),
        },
    )
    def create(self, request, *args, **kwargs):
        """
        メソッド名：カテゴリ作成\n
        メソッド: POST\n
        PATH: /api/categories/
        """
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="カテゴリ全体更新",
        description="カテゴリ情報を全体更新します。",
        responses={
            200: CategorySerializer,
            400: OpenApiResponse(
                description="バリデーションエラー",
                examples=[
                    OpenApiExample(
                        "カテゴリ名が空",
                        value={"name": ["カテゴリ名は必須です。"]},
                        response_only=True,
                    ),
                    OpenApiExample(
                        "同名カテゴリが既に存在",
                        value={
                            "name": ["この企業には既に同じ名前のカテゴリが存在します。"]
                        },
                        response_only=True,
                    ),
                    OpenApiExample(
                        "自己参照エラー",
                        value={
                            "parent_category": [
                                "カテゴリ自身を親カテゴリに設定することはできません。"
                            ]
                        },
                        response_only=True,
                    ),
                    OpenApiExample(
                        "循環参照エラー",
                        value={
                            "parent_category": [
                                "循環参照が発生するため、この親カテゴリは設定できません。"
                            ]
                        },
                        response_only=True,
                    ),
                    OpenApiExample(
                        "親カテゴリが異なる企業",
                        value={
                            "parent_category": [
                                "親カテゴリは同じ企業に属している必要があります。"
                            ]
                        },
                        response_only=True,
                    ),
                ],
            ),
            404: OpenApiResponse(
                description="カテゴリが見つかりません",
                examples=[
                    OpenApiExample(
                        "カテゴリが存在しない",
                        value={"detail": "見つかりませんでした。"},
                        response_only=True,
                    ),
                ],
            ),
            500: OpenApiResponse(
                description="サーバー内部エラー",
                examples=[
                    OpenApiExample(
                        "サーバーエラー",
                        value={"detail": "サーバー内部エラーが発生しました。"},
                        response_only=True,
                    ),
                ],
            ),
        },
    )
    def update(self, request, *args, **kwargs):
        """
        メソッド名：カテゴリ全体更新\n
        メソッド: PUT\n
        PATH: /api/categories/{id}/
        """
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="カテゴリ部分更新",
        description="カテゴリ情報を部分更新します。",
        responses={
            200: CategorySerializer,
            400: OpenApiResponse(
                description="バリデーションエラー",
                examples=[
                    OpenApiExample(
                        "カテゴリ名が空",
                        value={"name": ["カテゴリ名は必須です。"]},
                        response_only=True,
                    ),
                    OpenApiExample(
                        "同名カテゴリが既に存在",
                        value={
                            "name": ["この企業には既に同じ名前のカテゴリが存在します。"]
                        },
                        response_only=True,
                    ),
                    OpenApiExample(
                        "自己参照エラー",
                        value={
                            "parent_category": [
                                "カテゴリ自身を親カテゴリに設定することはできません。"
                            ]
                        },
                        response_only=True,
                    ),
                    OpenApiExample(
                        "循環参照エラー",
                        value={
                            "parent_category": [
                                "循環参照が発生するため、この親カテゴリは設定できません。"
                            ]
                        },
                        response_only=True,
                    ),
                ],
            ),
            404: OpenApiResponse(
                description="カテゴリが見つかりません",
                examples=[
                    OpenApiExample(
                        "カテゴリが存在しない",
                        value={"detail": "見つかりませんでした。"},
                        response_only=True,
                    ),
                ],
            ),
            500: OpenApiResponse(
                description="サーバー内部エラー",
                examples=[
                    OpenApiExample(
                        "サーバーエラー",
                        value={"detail": "サーバー内部エラーが発生しました。"},
                        response_only=True,
                    ),
                ],
            ),
        },
    )
    def partial_update(self, request, *args, **kwargs):
        """
        メソッド名：カテゴリ部分更新\n
        メソッド: PATCH\n
        PATH: /api/categories/{id}/
        """
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="カテゴリ削除",
        description="IDを指定してカテゴリを削除します。",
        responses={
            204: OpenApiResponse(description="削除成功"),
            404: OpenApiResponse(
                description="カテゴリが見つかりません",
                examples=[
                    OpenApiExample(
                        "カテゴリが存在しない",
                        value={"detail": "見つかりませんでした。"},
                        response_only=True,
                    ),
                ],
            ),
            500: OpenApiResponse(
                description="サーバー内部エラー",
                examples=[
                    OpenApiExample(
                        "サーバーエラー",
                        value={"detail": "サーバー内部エラーが発生しました。"},
                        response_only=True,
                    ),
                ],
            ),
        },
    )
    def destroy(self, request, *args, **kwargs):
        """
        メソッド名：カテゴリ削除\n
        メソッド: DELETE\n
        PATH: /api/categories/{id}/
        """
        return super().destroy(request, *args, **kwargs)
