"""The structure of a document: which paragraphs are titles of what level."""

import re
from dataclasses import dataclass
from typing import Protocol, final

from docx.document import Document
from docx.text.paragraph import Paragraph
from typing_extensions import override

from gost_espd_checker.effective import Lettering, Placement


class Outline(Protocol):
    """Paragraphs of a document, each with the level of its title."""

    def levels(self) -> tuple[tuple[Paragraph, int], ...]:
        """Pair every paragraph with 1 for a section, 2 for a subsection."""
        ...


def _level(paragraph: Paragraph, *, styled: bool) -> int:
    text = paragraph.text.strip()
    outline = Placement(paragraph).outline()
    numbered = (
        1
        if re.match(r"\d+\.\s+\S", text)
        else 2
        if re.match(r"\d+\.\d+\.?\s+\S", text)
        else 0
    )
    return (
        0
        if not re.search(r"\w", text)
        else outline + 1
        if styled and outline in {0, 1}
        else 0
        if styled
        else numbered
        if Lettering(paragraph).bold()
        else 0
    )


@final
@dataclass(frozen=True, slots=True)
class Headings(Outline):
    """Titles found by outline levels, or by bold numbered paragraphs."""

    document: Document

    @override
    def levels(self) -> tuple[tuple[Paragraph, int], ...]:
        """Level every paragraph of the body, leaving out lines of contents."""
        styled = any(
            Placement(paragraph).outline() in range(9)
            for paragraph in self.document.paragraphs
        )
        return tuple(
            (paragraph, _level(paragraph, styled=styled))
            for paragraph in self.document.paragraphs
            if not re.search(r"\t\s*\d+$", paragraph.text)
        )
