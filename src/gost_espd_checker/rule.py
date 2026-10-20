"""One requirement of a standard, as a check sees it."""

from typing import Protocol


class Rule(Protocol):
    """One requirement of a standard, with its clause and severity."""

    def line(self, place: str, message: str) -> str:
        """Render one violation of the rule."""
        ...
