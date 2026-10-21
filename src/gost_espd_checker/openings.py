"""Whether each paragraph of a document starts on a fresh page."""

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import final

from docx.document import Document
from docx.enum.section import WD_SECTION
from typing_extensions import override

from gost_espd_checker.breaks import Breaks


@final
@dataclass(frozen=True, slots=True)
class Openings(Iterable[bool]):
    """Paragraphs with nothing printed before them on their page."""

    _document: Document

    @override
    def __iter__(self) -> Iterator[bool]:
        """Follow page breaks, section breaks and empty paragraphs."""
        fresh, index = True, 0
        for paragraph in self._document.paragraphs:
            yield fresh
            if paragraph.paragraph_format.element.xpath("./w:pPr/w:sectPr"):
                index += 1
                fresh = self._document.sections[index].start_type not in {
                    WD_SECTION.CONTINUOUS,
                    WD_SECTION.NEW_COLUMN,
                }
            else:
                fresh = Breaks(paragraph).closes() or (
                    fresh and not paragraph.text.strip()
                )
