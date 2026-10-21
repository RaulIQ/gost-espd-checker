"""The place of the first name that matches a pattern."""

import re
from dataclasses import dataclass
from typing import SupportsInt, final

from typing_extensions import override


@final
@dataclass(frozen=True, slots=True)
class Spot(SupportsInt):
    """The index of a name like «АННОТАЦИЯ» among the names of lines."""

    _names: tuple[str, ...]
    _pattern: str

    @override
    def __int__(self) -> int:
        """Give the index of the first full match, ignoring case, or -1."""
        return next(
            (
                position
                for position, name in enumerate(self._names)
                if re.fullmatch(self._pattern, name, re.IGNORECASE)
            ),
            -1,
        )
