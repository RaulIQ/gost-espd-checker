"""The paragraph indent that starts every point and enumeration."""

import re
from dataclasses import dataclass
from typing import final

from docx.document import Document
from docx.text.paragraph import Paragraph
from typing_extensions import override

from gost_espd_checker.check import Check
from gost_espd_checker.effective import Effective, Placement
from gost_espd_checker.headings import Headings
from gost_espd_checker.rules import Catalog
from gost_espd_checker.violation import Violation


def _kind(paragraph: Paragraph) -> str:
    text = paragraph.text.strip()
    return (
        ""
        if not re.search(r"\w", text)
        else "пункт"
        if re.match(r"\d+(?:\.\d+)+\.\s+\S", text)
        else "перечисление"
        if re.match(r"(?:\d+[.)]|[-\u2013\u2014\u2022])\s+\S", text)
        or Placement(paragraph).listed()
        else ""
    )


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
                f"{_kind(paragraph)} «{paragraph.text.strip()[:40]}»",
                self.rules.rule("ESPD-106-07"),
                f"{_kind(paragraph)} начинается без абзацного отступа",
            )
            for paragraph, level in Headings(self.document).levels()
            if not level
            and _kind(paragraph)
            and Effective(paragraph).indent() <= 0
        )
