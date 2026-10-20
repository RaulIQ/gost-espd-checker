"""The numbers that may follow a number of a section or a point."""

from collections.abc import Container
from dataclasses import dataclass
from typing import final

from typing_extensions import override


@final
@dataclass(frozen=True, slots=True)
class Successors(Container[tuple[int, ...]]):
    """The next number at any depth, or the first one a level deeper."""

    before: tuple[int, ...]

    @override
    def __contains__(self, number: object) -> bool:
        """Check that the number continues the one before it."""
        return number in {
            (*self.before[:depth], self.before[depth] + 1)
            for depth in range(len(self.before))
        } | {(*self.before, 1)}
