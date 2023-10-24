from uuid import UUID
from datetime import datetime
from domain.entity.company import CompanyEntity
from typing import TypeVar, Optional

T = TypeVar("T", bound="CategoryEntity")

class CategoryEntity:
    def __init__(
            self,
            id: UUID,
            company: CompanyEntity,
            name: str,
            parent_category: Optional[T],
            created_at: datetime,
            updated_at: datetime,
            ):

        self.__validate_name(name)

        self.id: UUID = id
        self.company: CompanyEntity = company
        self.name: str = name
        self.parent_category: Optional[T] = parent_category
        self.created_at: datetime = created_at
        self.updated_at: datetime = updated_at

    @classmethod
    def new(
            cls,
            company: CompanyEntity,
            name: str,
            parent_category: Optional[T],
            ):
        """
        初めてエンティティが作成されるときに利用する
        """
        return cls(
            id=None,
            company=company,
            name=name,
            parent_category=parent_category,
            created_at=None,
            updated_at=None,
    )

    @classmethod
    def from_record(
            cls,
            id: UUID,
            company: CompanyEntity,
            name: str,
            parent_category: Optional[T],
            created_at: datetime,
            updated_at: datetime,
            ):
        """
        永続化された既存データからエンティティを作成する
        """
        return cls(
            id=id,
            company=company,
            name=name,
            parent_category=parent_category,
            created_at=created_at,
            updated_at=updated_at,
        )

    def __validate_name(self, name: str):
        """
        名前が255文字以下であるかを検証する
        """
        if len(name) > 255:
            raise ValueError("name must be 255 or less characters")

    def change_name(self, name: str):
        """
        名前を変更する
        """
        self.__validate_name(name)

        self.name = name

    def change_parent_category(self, parent_category: Optional[T]):
        """
        親カテゴリを変更する
        """
        self.parent_category = parent_category

    def change_company(self, company: CompanyEntity):
        """
        会社を変更する
        """
        self.company = company

    def to_dict(self):
        return {
            "id": str(self.id),
            "company": self.company.to_dict(),
            "name": self.name,
            "parent_category": self.parent_category.to_dict() if self.parent_category else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
