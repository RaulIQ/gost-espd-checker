"""The elements a paragraph inherits its formatting from."""

from collections.abc import Callable
from typing import Protocol

from docx.oxml.xmlchemy import BaseOxmlElement
from docx.text.font import Font


class Ancestry(Protocol):
    """A paragraph with the styles it inherits from, nearest first."""

    def owners(self) -> tuple[BaseOxmlElement, ...]:
        """List the paragraph and then the elements of its styles."""
        ...

    def flags(self, pick: Callable[[Font], bool | None]) -> tuple[bool, ...]:
        """Settle a font switch for every run with text; off when unset."""
        ...
