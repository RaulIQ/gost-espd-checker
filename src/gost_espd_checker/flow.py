"""Where a paragraph stands against the pages of a document."""

from typing import Protocol


class Flow(Protocol):
    """Where a paragraph sits against the pages of a document."""

    def opens(self) -> bool:
        """Whether a page break comes before any text of the paragraph."""
        ...

    def closes(self) -> bool:
        """Whether a page break comes after all text of the paragraph."""
        ...
