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

def __dataclass_transform__(
    *,
    eq_default: bool = True,
    order_default: bool = False,
    kw_only_default: bool = False,
    field_descriptors: Tuple[Union[type, Callable[..., Any]], ...] = (()),
) -> Callable[[_T], _T]:
    return lambda a: a


# From Sqlmodel, Slightly modified for msgspec
# def get_sqlalchemy_type(field:Type):
#     type_ = field
#     if is_optional_type(type_):
#         type_ = type_.__args__[0]

#     if issubclass(type_, float):
#         return Float()
#     if issubclass(type_, bool):
#         return Boolean()
#     if issubclass(type_, int):
#         return Integer()
#     if issubclass(type_, datetime):
#         return DateTime()
#     if issubclass(type_, date):
#         return Date()
#     if issubclass(type_, timedelta):
#         return Interval()
#     if issubclass(type_, time):
#         return Time()
#     if issubclass(type_, bytes):
#         return LargeBinary()
    
#     if issubclass(type_, str):
#         return AutoString()
#     raise RuntimeError("Undefined Type")
    
#     # if issubclass(type_, Decimal):
#     #     return Numeric(
#     #         precision=getattr(metadata, "max_digits", None),
#     #         scale=getattr(metadata, "decimal_places", None),
#     #     )


# # Attributes

# # Column()    Meta(extra={})

# def table_columns(cls:Type[_SQLTable]):
#     for f in fields(cls):
#         args = get_args(f.type)
#         if len(args) > 1:
#             meta_data = args[-1]
#             if isinstance(meta_data, Meta):
#                 # TODO: Automate creations of Unwritten Fields...
#                 column = meta_data.extra["__sqltable_column_info"]
#                 if isinstance(column, ColumnInfo):
#                     if column.sa_type is None:
#                         column.sa_type = get_sqlalchemy_type(args[0])
#                 else:
#                     # Relationship
#                     assert isinstance(column, RelationShipInfo)
                
#                 yield column.create(f.name)  
           
# def table(cls:Type[_SQLTable]) -> Type[_SQLTable]:
#     """Sets ups SQLAlchemy Columns and mapper arguments"""
#     for x in table_columns(cls):
#         cls._(cls, x.name, x)

#     return cls
    
    



default_registery = Registry()

# Inspired by SqlModel

class SQLTable(msgspec.Struct):
    metadata:ClassVar[MetaData] = default_registery.metadata
    registry:ClassVar[Registry] = default_registery
    __table__: ClassVar[FromClause]
    # __name__:ClassVar[str]
    # __mapper__:ClassVar[Mapper]
    # __abstract__:ClassVar[bool] = True
    # __allow_unmapped__:ClassVar[bool] = True

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


# def table(translation_hook:Optional[Callable[[inspect.Type], TypeDecorator]] = None):
#     def decorator():
#         def wrapper(cls:Type[_SQLTable]):
#             return setup_table_to_struct(cls, translation_hook)
#         return wrapper
#     return decorator()

def table(table:Type[_SQLTable], hook:Optional[Callable[[inspect.Type], TypeDecorator]] = None):
    """Declares an SQLTable Object as a usable table in your database

    :param table: An SQLTable class to declare
    :param hook: a custom callback object allowing one \
        to add custom SqlAlchemy Types and Msgspec Fields \
        to sqlalchemy
    """  
    return setup_table_to_struct(table, hook)


