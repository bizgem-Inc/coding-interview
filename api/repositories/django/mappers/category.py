from uuid import UUID

from api.domain.entities.category import Category
from api.domain.new_types.category_id import CategoryId
from api.domain.new_types.company_id import CompanyId
from api.repositories.django.orm_models.category import CategoryModel
from api.repositories.django.orm_models.company import CompanyModel


def to_domain(model: CategoryModel) -> Category:
    return Category(
        id=CategoryId(UUID(str(model.id))),  # type: ignore[arg-type]
        company_id=CompanyId(UUID(str(model.company_id))),  # type: ignore[arg-type]
        name=model.name,  # type: ignore[arg-type]
        parent_category_id=CategoryId(UUID(str(model.parent_category_id))) if model.parent_category_id else None,  # type: ignore[arg-type]
        created_at=model.created_at,  # type: ignore[arg-type]
        updated_at=model.updated_at,  # type: ignore[arg-type]
    )


def to_model(entity: Category, company: CompanyModel) -> CategoryModel:
    parent = (
        CategoryModel.objects.get(id=entity.parent_category_id)
        if entity.parent_category_id
        else None
    )
    return CategoryModel(
        id=entity.id,
        company=company,
        name=entity.name,
        parent_category=parent,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )
