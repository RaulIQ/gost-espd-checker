"""The structure of a document: which paragraphs are titles of what level."""

import re
from dataclasses import dataclass
from typing import final

from docx.document import Document
from docx.text.paragraph import Paragraph
from typing_extensions import override

from gost_espd_checker.level import Level
from gost_espd_checker.lineage import Lineage
from gost_espd_checker.outline import Outline
from gost_espd_checker.placement import Placement


@final
@dataclass(frozen=True, slots=True)
class Headings(Outline):
    """Titles found by outline levels, or by bold numbered paragraphs."""

    document: Document

    @override
    def levels(self) -> tuple[tuple[Paragraph, int], ...]:
        """Level every paragraph of the body, leaving out lines of contents."""
        styled = any(
            Placement(Lineage(paragraph)).outline() in range(9)
            for paragraph in self.document.paragraphs
        )
        return tuple(
            (paragraph, int(Level(paragraph, styled=styled)))
            for paragraph in self.document.paragraphs
            if not re.search(r"\t\s*\d+$", paragraph.text)
        )
