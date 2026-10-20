"""The titles of a document with their levels."""

from typing import Protocol

from docx.text.paragraph import Paragraph


class Outline(Protocol):
    """Paragraphs of a document, each with the level of its title."""

    def levels(self) -> tuple[tuple[Paragraph, int], ...]:
        """Pair every paragraph with 1 for a section, 2 for a subsection."""
        ...
