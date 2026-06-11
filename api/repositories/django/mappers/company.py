from uuid import UUID

from api.domain.entities.company import Company
from api.domain.new_types.company_id import CompanyId
from api.repositories.django.orm_models.company import CompanyModel


def to_domain(model: CompanyModel) -> Company:
    return Company(
        id=CompanyId(UUID(str(model.id))),  # type: ignore[arg-type]
        name=model.name,  # type: ignore[arg-type]
        created_at=model.created_at,  # type: ignore[arg-type]
        updated_at=model.updated_at,  # type: ignore[arg-type]
    )


def to_model(entity: Company) -> CompanyModel:
    return CompanyModel(
        id=entity.id,
        name=entity.name,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )
