import uuid as _uuid

from typing import Optional

from django.db import IntegrityError, transaction
from rest_framework import status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from api.application.dto.category import (
    CreateCategoryRequest,
    UpdateCategoryRequest,
)
from api.application.use_cases.category.create import CreateCategory
from api.application.use_cases.category.delete import DeleteCategory
from api.application.use_cases.category.get import GetCategory
from api.application.use_cases.category.list import ListCategories
from api.application.use_cases.category.update import UpdateCategory
from api.domain.exceptions import (
    CategoryNotFoundError,
    CompanyNotFoundError,
    DuplicateCategoryNameError,
    ReferencedCategoryNotFoundError,
)
from api.domain.new_types.category_id import CategoryId
from api.repositories.django.category import DjangoCategoryRepository
from api.services.web.serializers.category import (
    CategoryInputSerializer,
    CategoryOutputSerializer,
    CategoryPartialInputSerializer,
    handle_domain_error,
)


class CategoryViewSet(viewsets.ViewSet):
    """Category CRUDのHTTP境界。

    ViewがComposition RootとしてRepositoryとUse Caseを組み立てる。
    独自CRUD実装のためViewSetを使用する。
    """

    def _get_repository(self):
        return DjangoCategoryRepository()

    @staticmethod
    def _validate_uuid(pk: Optional[str]) -> Response | None:
        """URLのUUIDパラメータを検証する。不正な形式なら400を返す。"""
        if pk is None:
            return Response({"detail": "Invalid UUID format."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            _uuid.UUID(pk)
        except (ValueError, AttributeError):
            return Response({"detail": "Invalid UUID format."}, status=status.HTTP_400_BAD_REQUEST)
        return None

    def list(self, request: Request) -> Response:
        limit = self._parse_limit(request.query_params.get("limit"))
        page = self._parse_page(request.query_params.get("page"))
        offset = (page - 1) * limit

        repository = self._get_repository()
        use_case = ListCategories(repository)
        result = use_case.execute(limit=limit, offset=offset)
        return Response([self._serialize(r) for r in result])

    @staticmethod
    def _parse_limit(value: Optional[str]) -> int:
        if value is None:
            return 10
        try:
            limit = int(value)
            if limit < 1:
                return 10
            return min(limit, 100)
        except (ValueError, TypeError):
            return 10

    @staticmethod
    def _parse_page(value: Optional[str]) -> int:
        if value is None:
            return 1
        try:
            page = int(value)
            return min(max(page, 1), 1_000_000)
        except (ValueError, TypeError):
            return 1

    def retrieve(self, request: Request, pk: Optional[str] = None) -> Response:
        invalid = self._validate_uuid(pk)
        if invalid is not None:
            return invalid
        repository = self._get_repository()
        use_case = GetCategory(repository)
        try:
            result = use_case.execute(CategoryId(_uuid.UUID(pk)))
            return Response(self._serialize(result))
        except CategoryNotFoundError:
            return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request: Request) -> Response:
        input_serializer = CategoryInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        domain_ids = input_serializer.to_domain_ids()

        repository = self._get_repository()
        use_case = CreateCategory(repository)
        req = CreateCategoryRequest(**domain_ids)

        try:
            with transaction.atomic():
                result = use_case.execute(req)
            return Response(self._serialize(result), status=status.HTTP_201_CREATED)
        except (ReferencedCategoryNotFoundError, CompanyNotFoundError, DuplicateCategoryNameError) as exc:
            err = handle_domain_error(exc)
            return Response(err.detail, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            # 並行リクエストによるDB制約違反
            return Response({"name": ["Duplicate category name in this company."]}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request: Request, pk: Optional[str] = None) -> Response:
        invalid = self._validate_uuid(pk)
        if invalid is not None:
            return invalid
        input_serializer = CategoryInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        domain_ids = input_serializer.to_domain_ids()

        repository = self._get_repository()
        use_case = UpdateCategory(repository)
        req = UpdateCategoryRequest(**domain_ids)

        try:
            with transaction.atomic():
                result = use_case.execute(CategoryId(_uuid.UUID(pk)), req)
            return Response(self._serialize(result))
        except CategoryNotFoundError:
            return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
        except (CompanyNotFoundError, ReferencedCategoryNotFoundError, DuplicateCategoryNameError) as exc:
            err = handle_domain_error(exc)
            return Response(err.detail, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            # 並行リクエストによるDB制約違反
            return Response({"name": ["Duplicate category name in this company."]}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request: Request, pk: Optional[str] = None) -> Response:
        invalid = self._validate_uuid(pk)
        if invalid is not None:
            return invalid

        # 入力検証はトランザクション外で実行（明示的なnullも検証対象）
        partial_serializer = CategoryPartialInputSerializer(data=request.data)
        partial_serializer.is_valid(raise_exception=True)
        partial_data = partial_serializer.validated_data

        repository = self._get_repository()

        # 取得、マージ、保存を同一トランザクション内で行う
        try:
            with transaction.atomic():
                get_use_case = GetCategory(repository)
                existing = get_use_case.execute(CategoryId(_uuid.UUID(pk)))

                # 検証済みの値だけを既存値とマージ
                merged_data = {
                    "company_id": str(existing.company_id),
                    "name": existing.name,
                    "parent_category_id": existing.parent_category_id,
                }
                if "company_id" in partial_data:
                    merged_data["company_id"] = str(partial_data["company_id"])
                if "name" in partial_data:
                    merged_data["name"] = partial_data["name"]
                if "parent_category_id" in partial_data:
                    merged_data["parent_category_id"] = partial_data["parent_category_id"]

                input_serializer = CategoryInputSerializer(data=merged_data)
                input_serializer.is_valid(raise_exception=True)
                domain_ids = input_serializer.to_domain_ids()

                update_use_case = UpdateCategory(repository)
                req = UpdateCategoryRequest(**domain_ids)
                result = update_use_case.execute(CategoryId(_uuid.UUID(pk)), req)
            return Response(self._serialize(result))
        except CategoryNotFoundError:
            return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
        except (CompanyNotFoundError, ReferencedCategoryNotFoundError, DuplicateCategoryNameError) as exc:
            err = handle_domain_error(exc)
            return Response(err.detail, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            # 並行リクエストによるDB制約違反
            return Response({"name": ["Duplicate category name in this company."]}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request: Request, pk: Optional[str] = None) -> Response:
        invalid = self._validate_uuid(pk)
        if invalid is not None:
            return invalid
        repository = self._get_repository()
        use_case = DeleteCategory(repository)

        try:
            with transaction.atomic():
                use_case.execute(CategoryId(_uuid.UUID(pk)))
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CategoryNotFoundError:
            return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def _serialize(response) -> dict:  # type: ignore[return-value]
        return CategoryOutputSerializer(response).data
