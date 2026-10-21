"""The paragraph indent that starts every point and enumeration."""

from dataclasses import dataclass
from typing import final

from docx.document import Document
from typing_extensions import override

from gost_espd_checker.catalog import Catalog
from gost_espd_checker.check import Check
from gost_espd_checker.effective import Effective
from gost_espd_checker.headings import Headings
from gost_espd_checker.kind import Kind
from gost_espd_checker.lineage import Lineage
from gost_espd_checker.violation import Violation


@final
@dataclass(frozen=True, slots=True)
class Indents(Check):
    """Clause 2.1.6: every structural element starts with an indent."""

    document: Document
    rules: Catalog

    @override
    def violations(self) -> tuple[Violation, ...]:
        """Report points and enumerations whose first line is not indented."""
        return tuple(
            Violation(
                f"{Kind(paragraph)} «{paragraph.text.strip()[:40]}»",
                self.rules.rule("ESPD-106-07"),
                f"{Kind(paragraph)} начинается без абзацного отступа",
            )
            for paragraph, level in Headings(self.document).levels()
            if not level
            and str(Kind(paragraph))
            and Effective(Lineage(paragraph)).indent() <= 0
        )
