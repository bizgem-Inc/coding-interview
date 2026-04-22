import uuid
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from api.models import Category, Company
from api.serializers.category import CategoriesSerializer


class CategoryView(APIView):
    """
    カテゴリのリソースを操作するビュー。
    CRUD操作に加え、ツリー構造への変換や高度な削除バリデーションを提供する。
    """

    def _get_company(self, company_id: str) -> Company:
        """URLパスのUUIDを検証し、企業を取得する。"""
        try:
            u_id = uuid.UUID(company_id)
        except ValueError:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Invalid company_id format.")
        return get_object_or_404(Company, id=u_id)

    def _convert_to_tree(self, categories: list[dict]) -> list[dict]:
        """フラットなカテゴリリストを親子関係のツリー構造に変換する。"""
        category_map = {
            str(cat["id"]): {**cat, "children": []}
            for cat in categories
        }
        
        tree = []
        for cat in categories:
            cat_id_str = str(cat["id"])
            parent_id = cat["parent_category_id"]
            current = category_map[cat_id_str]

            if parent_id is None:
                tree.append(current)
            else:
                parent_id_str = str(parent_id)
                parent = category_map.get(parent_id_str)
                if parent:
                    parent["children"].append(current)
                else:
                    # 親がリストに含まれない（異常データまたはフィルタリング結果）場合はルートに置く
                    tree.append(current)
        return tree

    def get(self, request, company_id: str, category_id: str | None = None) -> Response:
        """
        カテゴリの一覧（ツリー形式）、または特定カテゴリの詳細を取得する。
        """
        company = self._get_company(company_id)

        if category_id:
            # 詳細取得：指定カテゴリとその直下の子を含むサブツリー
            try:
                u_cat_id = uuid.UUID(category_id)
            except ValueError:
                return Response({"detail": "Invalid category_id format."}, status=status.HTTP_400_BAD_REQUEST)

            queryset = Category.objects.filter(
                Q(id=u_cat_id) | Q(parent_category_id=u_cat_id),
                company=company
            )
            serializer = CategoriesSerializer(queryset, many=True, context={"company_id": company.id})
            
            tree = self._convert_to_tree(serializer.data)
            # 指定したIDのノードを特定して返す
            target = next((node for node in tree if str(node["id"]) == str(u_cat_id)), None)
            if not target:
                return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
            return Response(target)
        else:
            # 一覧取得：企業に属する全カテゴリをツリー形式で取得
            queryset = Category.objects.filter(company=company)
            serializer = CategoriesSerializer(queryset, many=True, context={"company_id": company.id})
            return Response({"categories": self._convert_to_tree(serializer.data)})

    def post(self, request, company_id: str) -> Response:
        """
        カテゴリを新規作成する。
        """
        company = self._get_company(company_id)
        serializer = CategoriesSerializer(data=request.data, context={"company_id": company.id})
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            serializer.save(company=company)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def patch(self, request, company_id: str, category_id: str) -> Response:
        """
        カテゴリを部分更新する。
        """
        company = self._get_company(company_id)
        category = get_object_or_404(Category, id=category_id, company=company)
        
        serializer = CategoriesSerializer(
            category, 
            data=request.data, 
            partial=True, 
            context={"company_id": company.id}
        )
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            serializer.save()
            
        return Response(serializer.data)

    def delete(self, request, company_id: str, category_id: str) -> Response:
        """
        カテゴリを削除する。
        独自仕様：子カテゴリが存在する場合、そのIDリストと共に削除を拒否する。
        """
        company = self._get_company(company_id)
        category = get_object_or_404(Category, id=category_id, company=company)

        # 子カテゴリの存在確認
        child_ids = list(Category.objects.filter(parent_category_id=category.id).values_list('id', flat=True))
        
        if child_ids:
            return Response(
                {
                    "detail": "Cannot delete category with children.",
                    "blocking_child_ids": child_ids
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            category.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
