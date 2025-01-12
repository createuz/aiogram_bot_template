import secrets
from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, BigInteger, DateTime, Enum, Boolean
from sqlalchemy.orm import mapped_column, Mapped

from db.models import Base
from db.structures.data_structure import Role


def generate_uid() -> str:
    return secrets.token_hex(3)


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uid: Mapped[str] = mapped_column(String(10), default=generate_uid, unique=True, index=True, nullable=False)
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_premium: Mapped[bool] = mapped_column(Boolean, nullable=False)
    language: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.USER)
    added_by: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
