from injector import inject
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import QuerySet

from api.models import Category
from api.inputs.category import (
    CategoryListInput,
    CategoryDetailInput,
    CategoryCreateInput,
    CategoryUpdateInput,
    CategoryDeleteInput,
)


class CategoryRepository:
    """カテゴリのリポジトリ"""

    def get_all(self) -> QuerySet:
        return Category.objects.all()

    def get_by_id(self, pk: int) -> Category | None:
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return None

    def filter_by_company(self, queryset: QuerySet, company_id: int) -> QuerySet:
        return queryset.filter(company_id=company_id)

    def filter_by_parent(self, queryset: QuerySet, parent_id: int) -> QuerySet:
        return queryset.filter(parent_category_id=parent_id)

    def filter_by_name(self, queryset: QuerySet, name: str) -> QuerySet:
        return queryset.filter(name__icontains=name)

    def search_by_name(self, queryset: QuerySet, search: str) -> QuerySet:
        return queryset.filter(name__icontains=search)

    def order_by(self, queryset: QuerySet, ordering: str) -> QuerySet:
        if ordering and ordering.replace("-", "") in [
            "name",
            "created_at",
            "updated_at",
        ]:
            return queryset.order_by(ordering)
        return queryset

    def has_children(self, category: Category) -> bool:
        return Category.objects.filter(parent_category=category).exists()

    @transaction.atomic
    def create(self, data: dict) -> Category:
        return Category.objects.create(**data)

    @transaction.atomic
    def update(self, category: Category, data: dict) -> Category:
        for key, value in data.items():
            if value is not None:
                setattr(category, key, value)
        category.save()
        return category

    @transaction.atomic
    def delete(self, category: Category) -> None:
        category.delete()


class ListCategoriesUseCase:
    """カテゴリ一覧取得のユースケース"""

    @inject
    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    def execute(self, input_data: CategoryListInput) -> dict:
        queryset = self.repository.get_all()

        # フィルタリング
        if input_data.company:
            queryset = self.repository.filter_by_company(queryset, input_data.company)
        if hasattr(input_data, "name") and input_data.name:
            queryset = self.repository.filter_by_name(queryset, input_data.name)
        if input_data.parent_category:
            queryset = self.repository.filter_by_parent(queryset, input_data.parent_category)

        # 並び替え
        queryset = self.repository.order_by(queryset, input_data.ordering)

        # ページネーション
        if input_data.page and input_data.page_size:
            paginator = Paginator(queryset, input_data.page_size)
            page = paginator.get_page(input_data.page)

            return {
                "count": paginator.count,
                "next": page.has_next(),
                "previous": page.has_previous(),
                "results": page.object_list,
            }

        # ページネーションなし
        return {"results": queryset}


class GetCategoryDetailUseCase:
    """カテゴリ詳細取得のユースケース"""

    @inject
    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    def execute(self, input_data: CategoryDetailInput) -> Category | None:
        return self.repository.get_by_id(input_data.pk)


class CreateCategoryUseCase:
    """カテゴリ作成のユースケース"""

    @inject
    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    def execute(self, input_data: CategoryCreateInput) -> dict:
        try:
            data = {k: v for k, v in input_data.__dict__.items() if bool(v)}
            category = self.repository.create(data)
            return {"success": True, "data": category}
        except Exception as e:
            return {"success": False, "error": str(e)}


class UpdateCategoryUseCase:
    """カテゴリ更新のユースケース"""

    @inject
    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    def execute(self, input_data: CategoryUpdateInput) -> dict:
        category = self.repository.get_by_id(input_data.pk)
        if not category:
            return {"success": False, "error": "Category not found"}

        try:
            # pkを除外してデータを準備
            update_data = {k: v for k, v in input_data.__dict__.items() if k != "pk" and bool(v)}
            updated_category = self.repository.update(category, update_data)
            return {"success": True, "data": updated_category}
        except Exception as e:
            return {"success": False, "error": str(e)}


class DeleteCategoryUseCase:
    """カテゴリ削除のユースケース"""

    @inject
    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    def execute(self, input_data: CategoryDeleteInput) -> dict:
        category = self.repository.get_by_id(input_data.pk)
        if not category:
            return {"success": False, "error": "Category not found"}

        # 子カテゴリの存在チェック
        if self.repository.has_children(category):
            return {"success": False, "error": "子カテゴリがあるため削除できません。"}

        self.repository.delete(category)
        return {"success": True}
