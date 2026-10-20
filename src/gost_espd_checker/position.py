"""Where a paragraph stands in the structure of a document."""

from typing import Protocol


class Position(Protocol):
    """Where a paragraph stands in the structure of a document."""

    def outline(self) -> int:
        """Tell the outline level: 0 for a section, 9 for body text."""
        ...

    def listed(self) -> bool:
        """Whether the paragraph is an item of a Word list."""
        ...
