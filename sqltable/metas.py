from typing import Any, Mapping, Optional, Sequence, Type, Union, overload

from msgspec import Meta, Struct
from sqlalchemy import Column as _Column
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm.relationships import _RelationshipDeclared

# Inspired By SQLModel.


class RelationShipInfo(Struct):
    back_populates:str
    sa_relationship_args:Optional[Sequence[Any]] = None
    sa_relationship_kw:Optional[Mapping[str,Any]] = None
    # sa_type:Optional[Type] = None

    # TODO: Link Models?

    def create(self) -> _RelationshipDeclared:
        return relationship(back_populates=self.back_populates, *self.sa_relationship_args, **self.sa_relationship_kw)




@overload
def Relationship(
    *,
    back_populates:str,
    sa_relationship_args:Optional[Sequence[Any]] = None,
    sa_relationship_kw:Optional[Mapping[str,Any]] = None, 
    # TODO: Link Model like sqlmodel?

    gt: Union[int, float, None] = None,
    ge: Union[int, float, None] = None,
    lt: Union[int, float, None] = None,
    le: Union[int, float, None] = None,
    multiple_of: Union[int, float, None] = None,
    pattern: Union[str, None] = None,
    min_length: Union[int, None] = None,
    max_length: Union[int, None] = None,
    tz: Union[bool, None] = None,
    title: Union[str, None] = None,
    description: Union[str, None] = None,
    examples: Union[list, None] = None,
    extra_json_schema: Union[dict, None] = None,
    extra: Union[dict, None] = None,
) -> Meta:
    ...

def Relationship(
    *,
    back_populates:str,
    sa_relationship_args:Optional[Sequence[Any]] = None,
    sa_relationship_kw:Optional[Mapping[str,Any]] = None,

    **meta_kw
) -> Meta:
    if extra := meta_kw.get("extra"):
        extra["__sqltable_column_info"] = RelationShipInfo(back_populates, sa_relationship_args, sa_relationship_kw)
    else:
        meta_kw["extra"] = {}
        meta_kw["extra"] = {"__sqltable_column_info": RelationShipInfo(back_populates, sa_relationship_args, sa_relationship_kw)}

    return Meta(**meta_kw)


class NullType:
    """Meant to be a flag for sqlalchemy to override the nullable Columninfo argument"""
    def __init__(self, sa_type):
        self.sa_type = sa_type

class ColumnInfo(Struct):
    primary_key:Optional[bool] = None
    nullable:Optional[Any] = None
    foreign_key:Optional[str] = None
    unique:Optional[bool] = None
    index:Optional[bool] = None
    sa_type:Optional[Type] = None
    sa_column_args: Optional[Sequence[Any]] = None
    sa_column_kwargs: Optional[Mapping[str, Any]] = None

    # A Mirror of sqlmodel.main.get_column_from_field made smaller and more efficient
    def create(self, name:str):
        primary_key = True if self.primary_key else False
        index = True if self.index else False
        nullable = not primary_key and isinstance(self.sa_type, NullType)
        foreign_key = self.foreign_key
        unique = True if self.unique else False
        args = []
        
        if foreign_key:
            assert isinstance(foreign_key, str)
            args.append(ForeignKey(foreign_key))
    
        kw = {
            "primary_key": primary_key,
            "nullable": nullable,
            "index": index,
            "unique": unique,
        }

        if self.sa_column_args is not None:
            args.extend(list(self.sa_column_args))
        
        if self.sa_column_kwargs is not None:
            kw.update(self.sa_column_kwargs)

        if isinstance(self.sa_type, NullType):
            # Extract the real type...
            self.sa_type = self.sa_type.sa_type


        return _Column(name, self.sa_type, *args, **kw)


def Column(
    *,
    primary_key:Optional[bool] = None,
    nullable:Optional[Any] = None, 
    foreign_key:Optional[str] = None,
    unique:Optional[bool] = None,
    index:Optional[Any] = None,
    sa_type:Optional[Type] = None,
    sa_column_args: Optional[Sequence[Any]] = None,
    sa_column_kwargs: Optional[Mapping[str, Any]] = None,
    **meta_kw
) -> Meta:
    """Maps Object to Meta to be annotated upon"""

    __sqltable_column_info = ColumnInfo(primary_key, nullable, foreign_key, unique, index, sa_type, sa_column_args, sa_column_kwargs)
    if extra := meta_kw.get("extra"):
        extra["__sqltable_column_info"] = __sqltable_column_info
    else:
        meta_kw["extra"] = {}
        meta_kw["extra"] = {"__sqltable_column_info": __sqltable_column_info}

    return Meta(**meta_kw)


