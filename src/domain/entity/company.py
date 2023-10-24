from uuid import UUID
from datetime import datetime

class CompanyEntity:
    def __init__(
            self,
            id: UUID,
            name: str,
            created_at: datetime,
            updated_at: datetime,
            ):

        self.__validate_name(name)

        self.id: UUID = id
        self.name: str = name
        self.created_at: datetime = created_at
        self.updated_at: datetime = updated_at

    @classmethod
    def new(
            cls,
            name: str,
            ):
        """
        初めてエンティティが作成されるときに利用する
        """
        return cls(
            id=None,
            name=name,
            created_at=None,
            updated_at=None,
    )

    @classmethod
    def from_record(
            cls,
            id: UUID,
            name: str,
            created_at: datetime,
            updated_at: datetime,
            ):
        """
        永続化された既存データからエンティティを作成する
        """
        return cls(
            id=id,
            name=name,
            created_at=created_at,
            updated_at=updated_at,
        )

    def __validate_name(self, name: str):
        """
        名前が255文字以下であるかを検証する
        """
        if len(name) > 255:
            raise ValueError("name must be 255 or less characters")

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
