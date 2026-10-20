"""The margins of a section: forms 1 and 2 of GOST 19.106-78."""

from dataclasses import dataclass
from typing import final

from docx.section import Section
from docx.shared import Mm
from typing_extensions import override

from gost_espd_checker.check import Check
from gost_espd_checker.millimeters import Millimeters
from gost_espd_checker.rules import Catalog
from gost_espd_checker.violation import Violation


@final
@dataclass(frozen=True, slots=True)
class Margins(Check):
    """Clause 2.1.2: margins of 25, 20, 10 and 15 mm, to the twip."""

    section: Section
    number: int
    rules: Catalog

    @override
    def violations(self) -> tuple[Violation, ...]:
        """Every margin that differs from its norm or is missing."""
        return tuple(
            Violation(
                f"раздел {self.number}",
                self.rules.rule("ESPD-106-02"),
                f"{side} поле {Millimeters(margin)} вместо {norm} мм",
            )
            for side, margin, norm in (
                ("верхнее", self.section.top_margin, 25),
                ("левое", self.section.left_margin, 20),
                ("правое", self.section.right_margin, 10),
                ("нижнее", self.section.bottom_margin, 15),
            )
            if margin is None or margin.twips != Mm(norm).twips
        )
