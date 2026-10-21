"""The title of a section: capitals, centered."""

from dataclasses import dataclass
from typing import final

from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.text.paragraph import Paragraph
from typing_extensions import override

from gost_espd_checker.catalog import Catalog
from gost_espd_checker.check import Check
from gost_espd_checker.effective import Effective
from gost_espd_checker.lettering import Lettering
from gost_espd_checker.lineage import Lineage
from gost_espd_checker.violation import Violation


@final
@dataclass(frozen=True, slots=True)
class SectionTitle(Check):
    """Clause 2.1.7: a section title is in capitals and centered."""

    _paragraph: Paragraph
    _place: str
    _rules: Catalog

    @override
    def violations(self) -> tuple[Violation, ...]:
        """Report lowercase letters and an alignment other than centered."""
        formatting = Effective(Lineage(self._paragraph))
        return tuple(
            Violation(self._place, self._rules.rule(key), message)
            for key, message, broken in (
                (
                    "ESPD-106-08",
                    "заголовок раздела написан не прописными буквами",
                    any(letter.islower() for letter in self._paragraph.text)
                    and not Lettering(Lineage(self._paragraph)).capitals(),
                ),
                (
                    "ESPD-106-09",
                    "заголовок раздела не выровнен по центру",
                    formatting.alignment() != WD_PARAGRAPH_ALIGNMENT.CENTER,
                ),
            )
            if broken
        )
