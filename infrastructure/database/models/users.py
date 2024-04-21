from typing import Optional

from sqlalchemy import String, UUID, text
from sqlalchemy import BIGINT, Boolean, true
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column

from .base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = 'users'
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text('uuid_generate_v4()'))
    telegram_id: Mapped[int] = mapped_column(BIGINT, unique=True)
    username: Mapped[Optional[str]] = mapped_column(String(128))
    full_name: Mapped[str] = mapped_column(String(128))
    active: Mapped[bool] = mapped_column(Boolean, server_default=true())
    message_statistic: Mapped['MessageStatistic'] = relationship('MessageStatistic', uselist=False)
