"""The formatting of a paragraph as Word shows it, after styles apply."""

from dataclasses import dataclass
from typing import final

from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml.ns import qn
from docx.shared import Length, Twips
from typing_extensions import override

from gost_espd_checker.ancestry import Ancestry
from gost_espd_checker.formatting import Formatting


@final
@dataclass(frozen=True, slots=True)
class Effective(Formatting):
    """A paragraph whose properties fall back on its style and its bases."""

    lineage: Ancestry

    @override
    def alignment(self) -> WD_PARAGRAPH_ALIGNMENT:
        """Take the first alignment set; Word aligns left without one."""
        found = [
            value
            for owner in self.lineage.owners()
            for value in owner.xpath("./w:pPr/w:jc/@w:val")
        ]
        return WD_PARAGRAPH_ALIGNMENT.from_xml(
            {"start": "left", "end": "right"}.get(found[0], found[0])
            if found
            else "left"
        )

    @override
    def indent(self) -> Length:
        """Add the first line or hanging indent to the left one, like Word."""
        marks = [
            mark
            for owner in self.lineage.owners()
            for mark in owner.xpath("./w:pPr/w:ind")
        ]
        return Twips(
            next(
                (
                    int(value)
                    for mark in marks
                    for value in mark.xpath("@w:left | @w:start")[:1]
                ),
                0,
            )
            + next(
                (
                    -int(mark.get(qn("w:hanging")))
                    if mark.get(qn("w:hanging")) is not None
                    else int(mark.get(qn("w:firstLine")))
                    for mark in marks
                    if mark.get(qn("w:hanging")) is not None
                    or mark.get(qn("w:firstLine")) is not None
                ),
                0,
            )
        )

    @override
    def hyphenation(self) -> bool:
        """Allow hyphenation unless the paragraph or a style suppresses it."""
        found = [
            switch
            for owner in self.lineage.owners()
            for switch in owner.xpath("./w:pPr/w:suppressAutoHyphens")
        ]
        return not found or found[0].get(qn("w:val")) in {"0", "false", "off"}

    @override
    def pagebreak(self) -> bool:
        """Take the first page break before set; none without one."""
        found = [
            switch
            for owner in self.lineage.owners()
            for switch in owner.xpath("./w:pPr/w:pageBreakBefore")
        ]
        return bool(found) and found[0].get(qn("w:val")) not in {
            "0",
            "false",
            "off",
        }
