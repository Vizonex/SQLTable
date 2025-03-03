"""Import helper for sqlalchmey made for helping the json decoder with Mapped Variables"""
from sqlalchemy.orm import Mapped as _Mapped, mapped_column
from typing import TypeVar, Annotated, TYPE_CHECKING

T = TypeVar("T")

# HACK: msgspec doesn't like mapped variables for encoding so we
# need to do some shady stuff to Force it...
# Because otherwise we get msgspec.ValidationError: Expected `Mapped`, got `str` - at `$.[blah blah blah]`
if not TYPE_CHECKING:
    Mapped = Annotated[T, _Mapped[T]]
else:
    Mapped = _Mapped

