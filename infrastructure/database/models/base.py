import re
import datetime
from typing import Dict, Any, Pattern, Final, Optional

from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import registry, DeclarativeMeta, has_inherited_table
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql.functions import func
from typing_extensions import Annotated

int_pk = Annotated[int, mapped_column(primary_key=True)]

mapper_registry = registry()

TABLE_NAME_REGEX: Pattern[str] = re.compile(r"(?<=[A-Z])(?=[A-Z][a-z])|(?<=[^A-Z])(?=[A-Z])")
PLURAL: Final[str] = 's'


class Base(metaclass=DeclarativeMeta):
    __abstract__ = True
    __mapper_args__ = {'eager_defaults': True}
    __slots__ = ()

    def __init__(self, **kwargs: Any) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)

    registry = mapper_registry
    metadata = mapper_registry.metadata

    @classmethod
    def __tablename__(cls) -> Optional[str]:
        if has_inherited_table(cls):
            return None
        cls_name = cls.__qualname__
        table_name_parts = re.split(TABLE_NAME_REGEX, cls_name)
        formatted_table_name = ''.join(
            table_name_part.lower() + '_' for table_name_part in table_name_parts
        )
        last_underscore = formatted_table_name.rfind('_')
        return f"{formatted_table_name[:last_underscore]}{PLURAL}"

    def _get_attributes(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

    def __str__(self) -> str:
        attrs = '|'.join(str(v) for v in self._get_attributes().values())
        return f"{self.__class__.__qualname__} {attrs}"

    def __repr__(self) -> str:
        table_attrs = inspect(self).attrs
        primary_keys = ' '.join(
            f"{key.name}={table_attrs[key.name].value}"
            for key in inspect(self.__class__).primary_key
        )
        return f"{self.__class__.__qualname__}->{primary_keys}"

    def as_dict(self) -> Dict[str, Any]:
        return self._get_attributes()


class TableNameMixin:
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )
