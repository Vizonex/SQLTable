from typing import Any, Callable, ClassVar, Optional, Tuple, TypeVar, Union, Type

import msgspec
from msgspec import inspect
from sqlalchemy.orm import declared_attr
from sqlalchemy.orm import registry as Registry
from sqlalchemy.sql.expression import FromClause
from sqlalchemy.sql.schema import MetaData
from sqlalchemy.types import TypeDecorator

from .table import struct_columns

_T = TypeVar("_T")
_SQLTable = TypeVar("_SQLTable", bound="SQLTable")

default_registery = Registry()

# Inspired by SQLModel

class SQLTable(msgspec.Struct):
    metadata:ClassVar[MetaData] = default_registery.metadata
    registry:ClassVar[Registry] = default_registery
    __table__: ClassVar[FromClause]

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()



def setup_table_to_struct(model:Type[_SQLTable], serlize_hook:Optional[Callable[[inspect.Type], TypeDecorator]] = None) -> Type[_SQLTable]:
    columns = struct_columns(model, serlize_hook)
    for name, value in columns.items():
        setattr(model, name, value)
    # mapped builds the table out for us...
    model.registry.mapped(model)
    return model

def table(table:Type[_SQLTable], hook:Optional[Callable[[inspect.Type], TypeDecorator]] = None):
    """Declares an SQLTable Object as a usable table in your database

    :param table: An SQLTable class to declare
    :param hook: a custom callback object allowing one \
        to add custom SqlAlchemy Types and Msgspec Fields \
        to sqlalchemy
    """  
    return setup_table_to_struct(table, hook)


