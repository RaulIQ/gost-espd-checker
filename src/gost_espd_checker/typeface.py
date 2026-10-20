"""How the letters of a paragraph look."""

from typing import Protocol


class Typeface(Protocol):
    """How the letters of a paragraph look."""

    def capitals(self) -> bool:
        """Whether every run of text is shown in capitals."""
        ...

    def bold(self) -> bool:
        """Whether every run of text is bold."""
        ...
