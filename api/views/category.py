from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from injector import Injector
from drf_yasg.utils import swagger_auto_schema
from api.serializers.category import CategoryListSerializer, CategoryDetailSerializer
from api.schemas.category import (
    category_list_params,
    category_list_response,
    category_detail_response,
)
from api.inputs.category import (
    CategoryListInput,
    CategoryDetailInput,
    CategoryCreateInput,
    CategoryUpdateInput,
    CategoryDeleteInput,
)
from api.use_cases.category import (
    ListCategoriesUseCase,
    GetCategoryDetailUseCase,
    CreateCategoryUseCase,
    UpdateCategoryUseCase,
    DeleteCategoryUseCase,
    CategoryRepository,
)


# Injectorの設定
def configure_injector():
    injector = Injector()
    injector.binder.bind(CategoryRepository, to=CategoryRepository)
    return injector


class CategoryListAPIView(APIView):
    """
    カテゴリ一覧の取得と新規作成を処理するビュー
    """

    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.injector = configure_injector()

    @swagger_auto_schema(
        operation_description="カテゴリの一覧を取得します",
        operation_summary="カテゴリ一覧取得",
        manual_parameters=category_list_params,
        responses={200: category_list_response, 400: "Bad Request"},
        tags=["categories"],
    )
    def get(self, request):
        """
        カテゴリの一覧取得
        """
        query_params = request.query_params.dict()
        input_data = CategoryListInput(**query_params)
        use_case = self.injector.get(ListCategoriesUseCase)
        result = use_case.execute(input_data)
        if "results" in result:
            result["results"] = CategoryListSerializer(result["results"], many=True).data
        return Response(result)

    @swagger_auto_schema(
        operation_description="新しいカテゴリを作成します",
        operation_summary="カテゴリ作成",
        request_body=CategoryDetailSerializer,
        responses={201: "Created (no body)", 400: "Bad Request"},
        tags=["categories"],
    )
    def post(self, request):
        """
        新規カテゴリの作成
        """
        # リクエストデータをシリアライズ
        serializer = CategoryDetailSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 入力データを作成
        input_data = CategoryCreateInput(**serializer.validated_data)
        use_case = self.injector.get(CreateCategoryUseCase)
        result = use_case.execute(input_data)
        if not result["success"]:
            return Response({"detail": result["error"]}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_201_CREATED)


class CategoryDetailAPIView(APIView):
    """
    特定のカテゴリの詳細操作用ビュー
    """

    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.injector = configure_injector()

    @swagger_auto_schema(
        operation_description="特定のカテゴリの詳細を取得します",
        operation_summary="カテゴリ詳細取得",
        responses={200: category_detail_response, 404: "Not Found"},
        tags=["categories"],
    )
    def get(self, request, pk):
        """特定のカテゴリの詳細を取得"""
        input_data = CategoryDetailInput(pk=pk)
        use_case = self.injector.get(GetCategoryDetailUseCase)
        result = use_case.execute(input_data)
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serialized_data = CategoryDetailSerializer(result).data
        return Response(serialized_data)

    @swagger_auto_schema(
        operation_description="カテゴリを完全更新します",
        operation_summary="カテゴリ完全更新",
        request_body=CategoryDetailSerializer,
        responses={204: "No Content", 400: "Bad Request", 404: "Not Found"},
        tags=["categories"],
    )
    def put(self, request, pk):
        """カテゴリ完全更新"""

        # 既存のカテゴリを取得
        input_data = CategoryDetailInput(pk=pk)
        use_case = self.injector.get(GetCategoryDetailUseCase)
        existing_category = use_case.execute(input_data)
        if existing_category is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # 更新予定のデータをシリアライズ
        serializer = CategoryDetailSerializer(
            existing_category, data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 更新用の入力データを作成
        input_data = CategoryUpdateInput(pk=pk, **serializer.validated_data)
        use_case = self.injector.get(UpdateCategoryUseCase)
        result = use_case.execute(input_data)
        if not result["success"]:
            return Response({"detail": result["error"]}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_description="カテゴリを削除します",
        operation_summary="カテゴリ削除",
        responses={204: "No Content"},
        tags=["categories"],
    )
    def delete(self, request, pk):
        """カテゴリ削除"""
        input_data = CategoryDeleteInput(pk=pk)
        use_case = self.injector.get(DeleteCategoryUseCase)
        use_case.execute(input_data)
        return Response(status=status.HTTP_204_NO_CONTENT)
