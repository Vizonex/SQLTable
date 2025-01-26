"""
Table Creation for SQLTable...
"""

from typing import Callable, Optional

import sqlalchemy
from msgspec import Struct, inspect
from sqlalchemy.types import TypeDecorator

from .metas import ColumnInfo, NullType, RelationShipInfo
from .sqltypes import AutoString


def serlize_type(type:inspect.Type, serlize_hook:Optional[Callable[[inspect.Type], TypeDecorator]] = None):
    """Turns Msgspec Inspection Types into an sqlalchemy types

    """
    if serlize_hook:
        sa_type = serlize_hook(type)
        # If the hook does not raise an error for undefined sqlalchemy types raise an error
        if sa_type is not None:
            if isinstance(sa_type, TypeDecorator):
                return sa_type
            raise ValueError(f"{sa_type.__class__.__name__} is not a sqlalchemy TypeDecorator")

    if isinstance(type, inspect.BoolType):
        return sqlalchemy.Boolean()
    
    elif isinstance(type, inspect.BytesType):
        return sqlalchemy.BLOB(length=type.max_length)

    # NOT Supported, Yet...
    # elif isinstance(type, inspect.CollectionType):

    if isinstance(type, inspect.DateTimeType):
        return sqlalchemy.DateTime(timezone=type.tz or False)

    # TODO: Fixes for DecimalType?
    elif isinstance(type, inspect.DecimalType):
        return sqlalchemy.DECIMAL()
    

    elif isinstance(type, inspect.DateType):
        return sqlalchemy.Date()

    elif isinstance(type, inspect.EnumType):
        # Thank you pep-345...
        return sqlalchemy.Enum(type.cls)
    
    elif isinstance(type, inspect.FloatType):
        return sqlalchemy.Float()
    
    elif isinstance(type, inspect.IntType):
        return sqlalchemy.Integer()

    elif isinstance(type, inspect.RawType):
        return sqlalchemy.BLOB()

    elif isinstance(type, inspect.StrType):
        if type.max_length is not None:
            return sqlalchemy.String(type.max_length)
        else:
            return AutoString()

    elif isinstance(type, inspect.UnionType):
        if type.includes_none:

            # Null needs inclusion, Luckily I made a special class just for defining it effieciently...
            return NullType(serlize_type(type.types[0]))
        else:
            raise ValueError("Union types other than \"None\" are not Supported")
    
    
    # TODO UUIDs...
    
    raise ValueError(f"{type.__name__} has no matching SQLAlchemy type")



def struct_columns(model:Struct, serlize_hook:Optional[Callable[[inspect.Type], TypeDecorator]] = None):
    """Converts msgspec.Struct Annotations into SqlAlchemy Columns
    
    :param model: a model to extract info from and convert field information into sql-columns for
    :param serlize_hook: A callback function for undefined types

    Function raises `ValueError` if types you provided are considered undefined or unreconized by
    the `serlize_type` function

    """
    model_type = inspect.type_info(model)
    assert isinstance(model_type, inspect.StructType)
    columns = {}
    for f in model_type.fields:
        
        if not isinstance(f.type, inspect.Metadata):
            col = ColumnInfo(sa_type=serlize_type(f.type, serlize_hook)).create(f.encode_name)
        
        # Depack metadata
        else:
            mtype = f.type
            col = None
            while isinstance(mtype, inspect.Metadata): 
                if column_info := mtype.extra.get("__sqltable_column_info"):
                    assert isinstance(column_info, (RelationShipInfo, ColumnInfo)), f"Class You Provided for __sqltable_column_info {column_info.__class__.__name__} is not supported yet"

                    if isinstance(column_info, ColumnInfo):
                        if not column_info.sa_type:
                            column_info.sa_type = serlize_type(mtype.type)

                        col = column_info.create(f.encode_name)
                    else:
                        col = column_info.create()
                    break

                else:
                    mtype = mtype.type

            # Extract type if no metadata info could be found...
            if col is None:
                col = ColumnInfo(sa_type=serlize_type(f.type, serlize_hook)).create(f.encode_name)
        
        columns[f.name] = col
    return columns
    




         



