"""The sheet of a section: A4 or A3 by GOST 19.106-78."""

from dataclasses import dataclass
from typing import final

from docx.section import Section
from docx.shared import Mm
from typing_extensions import override

from gost_espd_checker.catalog import Catalog
from gost_espd_checker.check import Check
from gost_espd_checker.millimeters import Millimeters
from gost_espd_checker.violation import Violation


@final
@dataclass(frozen=True, slots=True)
class PageSize(Check):
    """Clause 1.5: an A4 portrait sheet (form 1) or an A3 landscape one."""

    section: Section
    number: int
    rules: Catalog

    @override
    def violations(self) -> tuple[Violation, ...]:
        """Report the sheet unless it is A4 portrait or A3 landscape."""
        width, height = self.section.page_width, self.section.page_height
        if (width and width.twips, height and height.twips) in {
            (Mm(210).twips, Mm(297).twips),
            (Mm(420).twips, Mm(297).twips),
        }:
            return ()
        return (
            Violation(
                f"раздел {self.number}",
                self.rules.rule("ESPD-106-01"),
                f"лист {Millimeters(width)} на {Millimeters(height)} вместо"
                " A4 книжной ориентации или A3 альбомной",
            ),
        )
