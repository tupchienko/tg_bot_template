from datetime import datetime

from sqlalchemy import text, Column, UUID, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.models import Base


class MessageStatistic(Base):
    __tablename__ = 'message_statistics'
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text('uuid_generate_v4()'))
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    messages_total: Mapped[int] = mapped_column(Integer, default=0)
    messages_today: Mapped[int] = mapped_column(Integer, default=0)
    messages_hour: Mapped[int] = mapped_column(Integer, default=0)
    last_message_time: Mapped[datetime] = mapped_column(TIMESTAMP)

