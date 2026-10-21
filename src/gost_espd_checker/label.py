"""The place of an illustration or a table in a report."""

from dataclasses import dataclass
from typing import final

from typing_extensions import override


@final
@dataclass(frozen=True, slots=True)
class Label:
    """An element named by its caption, or by its count without one."""

    _kind: str
    _caption: str
    _position: int

    @override
    def __str__(self) -> str:
        """Render as «таблица «Таблица 2»» or «таблица 3 по порядку»."""
        return (
            f"{self._kind} «{self._caption}»"
            if self._caption
            else f"{self._kind} {self._position} по порядку"
        )
