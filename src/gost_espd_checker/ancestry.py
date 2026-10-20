"""The elements a paragraph inherits its formatting from."""

from typing import Protocol

from docx.oxml.xmlchemy import BaseOxmlElement
from docx.text.font import Font


class Ancestry(Protocol):
    """A paragraph with the styles it inherits from, nearest first."""

    def owners(self) -> tuple[BaseOxmlElement, ...]:
        """List the paragraph and then the elements of its styles."""
        ...

    def fonts(self) -> tuple[tuple[Font, ...], ...]:
        """List, for every run with text, its font and the fonts of styles."""
        ...
