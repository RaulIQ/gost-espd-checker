"""A style together with the styles it is based on."""

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import TypeVar, final

from docx.styles.style import CharacterStyle
from typing_extensions import override

_Style = TypeVar("_Style", bound=CharacterStyle)


@final
@dataclass(frozen=True, slots=True)
class Bases(Iterable[_Style]):
    """The chain of a style and its bases, nearest first."""

    _style: _Style | None

    @override
    def __iter__(self) -> Iterator[_Style]:
        """Walk from the style through every base style."""
        style = self._style
        while style is not None:
            yield style
            style = style.base_style
