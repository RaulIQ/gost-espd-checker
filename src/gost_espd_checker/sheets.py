"""Where sections of a document start: on a new sheet or not."""

from dataclasses import dataclass
from functools import partial
from itertools import accumulate
from typing import final

from docx.document import Document
from docx.enum.section import WD_SECTION
from docx.section import Sections
from docx.text.paragraph import Paragraph
from typing_extensions import override

from gost_espd_checker.breaks import Breaks
from gost_espd_checker.catalog import Catalog
from gost_espd_checker.check import Check
from gost_espd_checker.effective import Effective
from gost_espd_checker.headings import Headings
from gost_espd_checker.lineage import Lineage
from gost_espd_checker.violation import Violation


def _after(
    state: tuple[bool, int], paragraph: Paragraph, sections: Sections
) -> tuple[bool, int]:
    fresh, index = state
    if paragraph.paragraph_format.element.xpath("./w:pPr/w:sectPr"):
        return (
            sections[index + 1].start_type
            not in {WD_SECTION.CONTINUOUS, WD_SECTION.NEW_COLUMN},
            index + 1,
        )
    return (
        Breaks(paragraph).closes() or (fresh and not paragraph.text.strip())
    ), index


@final
@dataclass(frozen=True, slots=True)
class Sheets(Check):
    """Clause 2.1.7: every section is recommended to start on a new sheet."""

    document: Document
    rules: Catalog

    @override
    def violations(self) -> tuple[Violation, ...]:
        """Warn about section titles with text before them on the same page."""
        titles = {
            paragraph.paragraph_format.element
            for paragraph, level in Headings(self.document).levels()
            if level == 1
        }
        paragraphs = self.document.paragraphs
        return tuple(
            Violation(
                f"заголовок «{paragraph.text.strip()}»",
                self.rules.rule("ESPD-106-13"),
                "перед разделом нет перехода на новый лист",
            )
            for paragraph, (fresh, _) in zip(
                paragraphs,
                accumulate(
                    paragraphs,
                    partial(_after, sections=self.document.sections),
                    initial=(True, 0),
                ),
                strict=False,
            )
            if paragraph.paragraph_format.element in titles
            and not fresh
            and not Effective(Lineage(paragraph)).pagebreak()
            and not Breaks(paragraph).opens()
        )
