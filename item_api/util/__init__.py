import uuid
from typing import Optional


def uuid_of(value: str) -> Optional[uuid]:
    try:
        return uuid.UUID(value)  # UUIDとしてパース可能か確認
    except ValueError:
        return None
