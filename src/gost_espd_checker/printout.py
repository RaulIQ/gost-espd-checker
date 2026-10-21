"""A document as it falls into printed pages."""

from dataclasses import dataclass
from typing import final

from docx.document import Document
from docx.text.paragraph import Paragraph
from typing_extensions import override

from gost_espd_checker.breaks import Breaks
from gost_espd_checker.effective import Effective
from gost_espd_checker.leaves import Leaves
from gost_espd_checker.lineage import Lineage


@final
@dataclass(frozen=True, slots=True)
class Printout(Leaves):
    """Body paragraphs, tables, content controls and text boxes, by pages."""

    _document: Document

    @override
    def pages(self) -> tuple[tuple[Paragraph, ...], ...]:
        """Split on breaks and sections, skipping floating margin tables."""
        pages: list[list[Paragraph]] = [[]]
        for element in self._document.element.body.xpath(
            "./w:p | ./w:tbl[not(w:tblPr/w:tblpPr)]//w:p | ./w:sdt//w:p"
            " | ./w:p//w:txbxContent[not(ancestor::*[local-name()='Fallback'"
            " or local-name()='wgp'])]/w:p"
        ):
            paragraph = Paragraph(element, self._document)
            if pages[-1] and (
                Effective(Lineage(paragraph)).pagebreak()
                or Breaks(paragraph).opens()
            ):
                pages.append([])
            pages[-1].append(paragraph)
            if Breaks(paragraph).closes() or element.xpath("./w:pPr/w:sectPr"):
                pages.append([])
        return tuple(
            tuple(page)
            for page in pages
            if any(line.text.strip() for line in page)
        )
