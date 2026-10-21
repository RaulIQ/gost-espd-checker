"""The numbers of sections, subsections and points of a document."""

from dataclasses import dataclass
from typing import final

from docx.document import Document
from typing_extensions import override

from gost_espd_checker.catalog import Catalog
from gost_espd_checker.check import Check
from gost_espd_checker.dotted import Dotted
from gost_espd_checker.entries import Entries
from gost_espd_checker.successors import Successors
from gost_espd_checker.violation import Violation


@final
@dataclass(frozen=True, slots=True)
class Numbering(Check):
    """Clause 2.1.9: arabic numbers with a dot, running through a section."""

    document: Document
    rules: Catalog

    @override
    def violations(self) -> tuple[Violation, ...]:
        """Report numbers that break the run; titles without one restart it."""
        entries = tuple(Entries(self.document))
        return tuple(
            Violation(
                f"заголовок «{paragraph.text.strip()}»"
                if level
                else f"пункт «{paragraph.text.strip()[:40]}»",
                self.rules.rule("ESPD-106-17"),
                message,
            )
            for (paragraph, level, number, dotted), before in zip(
                entries,
                ((), *(entry[2] for entry in entries)),
                strict=False,
            )
            if number
            for message, broken in (
                (
                    (
                        f"номер {Dotted(number)} не продолжает нумерацию"
                        f" после {Dotted(before)}"
                    )
                    if before
                    else f"номер {Dotted(number)} вместо 1",
                    number not in Successors(before),
                ),
                (
                    (
                        f"номер {('раздела', 'подраздела')[level - 1]}"
                        f" {Dotted(number)} состоит не из"
                        f" {('одного числа', 'двух чисел')[level - 1]}"
                    ),
                    bool(level) and len(number) != level,
                ),
                (
                    f"после номера раздела {Dotted(number)} нет точки",
                    level == 1 and not dotted,
                ),
            )
            if broken
        )
