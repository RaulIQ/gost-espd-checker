"""Where sections of a document start: on a new sheet or not."""

from dataclasses import dataclass
from typing import final

from docx.document import Document
from typing_extensions import override

from gost_espd_checker.breaks import Breaks
from gost_espd_checker.catalog import Catalog
from gost_espd_checker.check import Check
from gost_espd_checker.effective import Effective
from gost_espd_checker.headings import Headings
from gost_espd_checker.lineage import Lineage
from gost_espd_checker.openings import Openings
from gost_espd_checker.violation import Violation


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
        return tuple(
            Violation(
                f"заголовок «{paragraph.text.strip()}»",
                self.rules.rule("ESPD-106-13"),
                "перед разделом нет перехода на новый лист",
            )
            for paragraph, fresh in zip(
                self.document.paragraphs, Openings(self.document), strict=True
            )
            if paragraph.paragraph_format.element in titles
            and not fresh
            and not Effective(Lineage(paragraph)).pagebreak()
            and not Breaks(paragraph).opens()
        )
