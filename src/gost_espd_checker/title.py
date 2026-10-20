"""What every title of a section or subsection must avoid."""

from dataclasses import dataclass
from typing import final

from docx.text.paragraph import Paragraph
from typing_extensions import override

from gost_espd_checker.check import Check
from gost_espd_checker.effective import Effective
from gost_espd_checker.rules import Catalog
from gost_espd_checker.violation import Violation


@final
@dataclass(frozen=True, slots=True)
class Title(Check):
    """Clause 2.1.7: no hyphens in a title and no period at its end."""

    paragraph: Paragraph
    place: str
    rules: Catalog
    hyphenation: bool

    @override
    def violations(self) -> tuple[Violation, ...]:
        """Report a period at the end, a soft hyphen and auto hyphenation."""
        text = self.paragraph.text.strip()
        return tuple(
            Violation(self.place, self.rules.rule(key), message)
            for key, message, broken in (
                (
                    "ESPD-106-11",
                    "в заголовке стоит перенос",
                    "\u00ad" in text,
                ),
                (
                    "ESPD-106-11",
                    "в заголовке разрешены автоматические переносы",
                    self.hyphenation
                    and Effective(self.paragraph).hyphenation(),
                ),
                (
                    "ESPD-106-12",
                    "в конце заголовка стоит точка",
                    text.endswith("."),
                ),
            )
            if broken
        )
