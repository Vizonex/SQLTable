from __future__ import annotations
from contextlib import contextmanager
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    List,
    Literal,
    Optional,
    Type,
    Union,
    get_args,
    overload,
)

from msgspec.json import Decoder as JsonDecoder
from msgspec.json import Encoder as JsonEncoder
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    DeclarativeBaseNoMeta,
    MappedAsDataclass,
    Mapper,
    declared_attr,
)
from sqlalchemy.orm.state import InstanceState
from sqlalchemy.sql import FromClause
from sqlalchemy.sql.base import _NoArg
from typing_extensions import Buffer, Self

# Some things were adopted/retained from SQLModel which include
# - __init_subclass__ table keyword to enable or disable an abstract able
# - __tablename__ was kept for simplicity and ease

# Some things were adopted from Msgspec
# - added JsonEncoder/JsonDecoders to SQLTable for Right-Away serlization

# class Interceptor:
#     def __setattr__(cls, key: str, value: Any) -> None:
#         print((key, value))
#         if "__mapper__" in cls.__dict__:
#             _add_attribute(cls, key, value)
#         else:
#             type.__setattr__(cls, key, value)

#     def __delattr__(cls, key: str) -> None:
#         if "__mapper__" in cls.__dict__:
#             _del_attribute(cls, key)
#         else:
#             type.__delattr__(cls, key)


class SQLTableDecoderMixin:
    """Special Json Decoder for SQLTable types"""

    if TYPE_CHECKING:
        __sqltable_decoder__: ClassVar[JsonDecoder[Self]]
        """Decodes Json Data into SQLTable Objects"""
        _sa_instance_state: ClassVar[InstanceState[Self]]

    @classmethod
    def remove_mapping_annotations(cls):
        """Temporarly alters annotations so msgspec can understand
        how to decode variables that are associated to `Mapped`"""
        __previous_annotations__ = cls.__annotations__.copy()

        for k, v in __previous_annotations__.items():
            # using type(v) would just give me _GenericAlias this bypasses that...
            if str(v).startswith("sqlalchemy.orm.base.Mapped"):
                # Unwrap SQLAlchemy Mapped varaibles temporarly
                # get_args comes from typing...
                cls.__annotations__[k] = get_args(v)[0]

        return __previous_annotations__

    @classmethod
    @contextmanager
    def temporarly_disable_mapped_annotations(cls):
        """
        Context Manager for helping create msgspec Decoders.
        By hacking the `Mapped` annotations in/out, it is possible to
        customize and add your own decoders into your SQLTable tables

        ::

            from msgspec.msgpack import Decoder as MsgpackDecoder

            class SQLMsgpackDecoder(SQLTableDecoderMixin):
                @classmethod
                def setup_up_msgpack_encoder(cls):
                    with cls.temporarly_disable_mapped_annotations():
                        self.__msgpack_decoder__ = MsgpackDecoder(type=cls)


        tip: you could wrap these custom functions you make using `__post_subclass__` for the best results...
        """

        old = cls.remove_mapping_annotations()
        yield
        # We're done playing trickery with msgspec so revert after were done building our decoder.
        cls.__annotations__ = old

    @classmethod
    def __init_decoder__(
        cls,
        dec_strict: bool = True,
        dec_hook: Optional[Callable[[type, Any], Any]] = None,
        dec_float_hook: Optional[Callable[[str], Any]] = None,
        **kw,
    ):
        """Initalizes the Sqltable decoder class"""

        # Until Msgspec gets around to fixing decoding we have to trick
        # it into thinking the items inside Mapped is our real variables we want to decode
        # # configure_mappers()

        with cls.temporarly_disable_mapped_annotations():
            cls.__sqltable_decoder__ = JsonDecoder(
                type=cls,
                strict=dec_strict,
                dec_hook=dec_hook,
                float_hook=dec_float_hook,
            )

        return None

    def __init_subclass__(
        cls,
        dec_strict: bool = True,
        dec_hook: Optional[Callable[[type, Any], Any]] = None,
        dec_float_hook: Optional[Callable[[str], Any]] = None,
        **kw,
    ):
        """
        :param dec_hook: hook for decoding unknown variable types
        :param dec_float_hook: hook for decoding float values
        :param dec_strict: hook for determining if unknown variable names should throw an error or not.
        :param kw: Other custom external keywords to use in your own abstract base...
        """
        super().__init_subclass__(**kw)

    @classmethod
    def decode(cls, buf: Union[Buffer, str]) -> Self:
        # setup _sa_instance_state ahead of time so that
        # unpickle events can access the object normally.
        # By looking into SQLModel's validable function it is possible
        # to figure out what we need to do to retain any if not all of
        # SQLTable's attributes...
        # Otherwise we will be missing a _sa_instance_state if not done...
        old_dict = cls.__dict__.copy()
        m = cls.__sqltable_decoder__.decode(buf)
        object.__setattr__(m, "__dict__", {**old_dict, **m.__dict__})
        return m

    @classmethod
    def decode_lines(cls, buf: Union[Buffer, str]) -> List[Self]:
        old_dict = cls.__dict__.copy()
        items = cls.__sqltable_decoder__.decode_lines(buf)
        for i in items:
            object.__setattr__(i, "__dict__", {**old_dict, **i.__dict__})
        return items


# NOTE: dataclasses are used to enable triggering msgspec into reconizing dataclass fields
class SQLTable(DeclarativeBaseNoMeta, MappedAsDataclass):
    """A Binding of msgspec that allows the user to bind msgspec Encoders and Decoders"""

    if TYPE_CHECKING:
        __name__: ClassVar[str]
        """The name of the Class"""
        __table__: ClassVar[FromClause]

        __mapper__: ClassVar[Mapper[Any]]

        __sqltable_encoder__: ClassVar[JsonEncoder]
        """Encodes SQLTables into Json"""

        __abstract__: ClassVar[bool]
        """Determines if we are an abstract table or not"""

        def __post_subclass__(cls, **kw):
            """Runs after `__init_subclass__` finishes
            You can use it to finalize any last class variables
            that you need"""

        __dataclass_fields__: ClassVar[dict[str, Any]]
        """The Dataclass fields that are in the `SQLTable`"""

    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls):
        return cls.__name__.lower()

    @overload
    def __init_subclass__(
        cls,
        table: bool = False,
        init: Union[_NoArg, bool] = _NoArg.NO_ARG,
        repr: Union[_NoArg, bool] = _NoArg.NO_ARG,  # noqa: A002
        eq: Union[_NoArg, bool] = _NoArg.NO_ARG,
        order: Union[_NoArg, bool] = _NoArg.NO_ARG,
        unsafe_hash: Union[_NoArg, bool] = _NoArg.NO_ARG,
        match_args: Union[_NoArg, bool] = _NoArg.NO_ARG,
        kw_only: Union[_NoArg, bool] = _NoArg.NO_ARG,
        dataclass_callable: Union[_NoArg, Callable[..., Type[Any]]] = _NoArg.NO_ARG,
        enc_hook: Optional[Callable[[Any], Any]] = None,
        enc_decimal_format: Literal["string", "number"] = "string",
        enc_uuid_format: Literal["canonical", "hex"] = "canonical",
        enc_order: Literal[None, "deterministic", "sorted"] = None,
        **kw: Any,
    ):
        """Enables binding of dataclasses to the Table

        :param table: if true table is not Abstract.
        :param init: Enable the creation of an init function
        :param repr: Generates a __repr__ dunder method
        :param eq: Generates a __eq__ dunder method
        :param order: Enables Order
        :param unsafe_hash: Allows for unsafe hashing
        :param match_args: Enables matching arguments
        :param kw_only: Forces all values in the dataclass to be keyword only variables
        :param dataclass_callable: Changes/Alters Class Creation. However if your using Pydantic please use SQLModel

        :param enc_hook: hook for encoding unknown variable types
        :param enc_decimal_format: options for Json Encoder's formatting of decimal values
        :param enc_uuid_format: options for Json Encoder's formatting of uuid values
        :param enc_order: options for Json Encoder's order

        :param kw: Other custom external keywords to use in your own abstract base...

        """

    @classmethod
    def __init_encoder__(
        cls,
        enc_hook: Optional[Callable[[Any], Any]] = None,
        enc_decimal_format: Literal["string", "number"] = "string",
        enc_uuid_format: Literal["canonical", "hex"] = "canonical",
        enc_order: Literal[None, "deterministic", "sorted"] = None,
        **kw,
    ):
        cls.__sqltable_encoder__ = JsonEncoder(
            enc_hook=enc_hook,
            decimal_format=enc_decimal_format,
            uuid_format=enc_uuid_format,
            order=enc_order,
        )

    @property
    def encoder(self) -> JsonEncoder:
        """Helper for encoding SQLTable to json format"""
        return self.__sqltable_encoder__

    def encode(self) -> bytes:
        """Encodes SQLTable Object to json"""
        return self.__sqltable_encoder__.encode(self)

    def encode_to(self, buffer: bytearray, offset: int = 0):
        self.__sqltable_encoder__.encode_into(self, buffer, offset)

    @classmethod
    def encode_lines(cls, items: List[Self]) -> bytes:
        return cls.__sqltable_encoder__.encode_lines(items)

    def __init_subclass__(cls, **kw):
        if kw.pop("table", False):
            # Enable Table Creation
            cls.__abstract__ = False

        # Decoder must be initalized first overwise what happens is that the instremented attributes
        # Screw us over...
        if hasattr(cls, "__init_decoder__"):
            cls.__init_decoder__(**kw)

        super().__init_subclass__(**kw)

        cls.__init_encoder__(cls, **kw)

        if hasattr(cls, "__post_subclass__"):
            cls.__post_subclass__(cls, **kw)


class AsyncSQLTable(AsyncAttrs, SQLTable):
    """Implements AsyncAttrs into `SQLTable`"""

    __abstract__ = True

