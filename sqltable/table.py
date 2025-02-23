from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    List,
    Literal,
    Optional,
    Protocol,
    Type,
    TypeVar,
    Union,
    overload,
    runtime_checkable,
)

from msgspec.json import Decoder as JsonDecoder
from msgspec.json import Encoder as JsonEncoder
from sqlalchemy.orm import (
    DeclarativeBaseNoMeta,
    Mapped,
    MappedAsDataclass,
    Mapper,
    declared_attr,
)
from sqlalchemy.sql import FromClause
from sqlalchemy.sql.base import _NoArg
from typing_extensions import Buffer, Self

# Some things were adopted/retained from SQLModel which include
# - __init_subclass__ table keyword to enable or disable an abstract able
# - __tablename__ was kept for simplicity and ease

# Some things were adopted from Msgspec
# - added JsonEncoder/JsonDecoders to SQLTable for Right-Away serlization


class SQLTableDecoderMixin:
    """Special Json Decoder for SQLTable types"""

    if TYPE_CHECKING:
        __sqltable_decoder__: ClassVar[JsonDecoder[Self]]
        """Decodes Json Data into SQLTable Objects"""

    @classmethod
    def __init_decoder__(
        cls,
        dec_strict: bool = True,
        dec_hook: Optional[Callable[[type, Any], Any]] = None,
        dec_float_hook: Optional[Callable[[str], Any]] = None,
        **kw,
    ):
        """Initalizes the Sqltable decoder class"""

        cls.__sqltable_decoder__ = JsonDecoder(
            type=cls, strict=dec_strict, dec_hook=dec_hook, float_hook=dec_float_hook
        )

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
        cls.__init_decoder__(dec_strict, dec_hook, dec_float_hook, **kw)

    @classmethod
    def decode(cls, buf: Union[Buffer, str]) -> Self:
        return cls.__sqltable_decoder__.decode(buf)

    @classmethod
    def decode_lines(cls, buf: Union[Buffer, str]) -> List[Self]:
        return cls.__sqltable_decoder__.decode_lines(buf)


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

        super().__init_subclass__(**kw)

        cls.__init_encoder__(cls, **kw)

        if hasattr(cls, "__post_subclass__"):
            cls.__post_subclass__(cls, **kw)
