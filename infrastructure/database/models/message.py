from sqlalchemy import Column, Integer, Text, ForeignKey, UUID, Enum
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.models import Base


class Message(Base):
    __tablename__ = "message_store"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    message: Mapped[str] = mapped_column(Text)
