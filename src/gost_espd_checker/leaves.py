"""The pages of a document."""

from typing import Protocol

from docx.text.paragraph import Paragraph


class Leaves(Protocol):
    """The pages of a document, each with its paragraphs in order."""

    def pages(self) -> tuple[tuple[Paragraph, ...], ...]:
        """Split the paragraphs into pages that carry some text."""
        ...
