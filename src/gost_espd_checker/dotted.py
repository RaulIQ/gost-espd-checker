"""A number of a section, subsection or point as the text shows it."""

from dataclasses import dataclass
from typing import final

from typing_extensions import override


@final
@dataclass(frozen=True, slots=True)
class Dotted:
    """The parts of a number, joined with dots."""

    _number: tuple[int, ...]

    @override
    def __str__(self) -> str:
        """Render as ``2.1.4``."""
        return ".".join(str(part) for part in self._number)
