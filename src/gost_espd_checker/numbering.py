"""The numbers of sections, subsections and points of a document."""

import re
from collections.abc import Iterator
from dataclasses import dataclass
from typing import final

from docx.document import Document
from docx.text.paragraph import Paragraph
from typing_extensions import override

from gost_espd_checker.check import Check
from gost_espd_checker.headings import Headings
from gost_espd_checker.rules import Catalog
from gost_espd_checker.violation import Violation


def _entries(
    document: Document,
) -> Iterator[tuple[Paragraph, int, tuple[int, ...], bool]]:
    for paragraph, level in Headings(document).levels():
        found = re.match(r"(\d+(?:\.\d+)*)(\.?)\s+\S", paragraph.text.strip())
        number = (
            tuple(int(part) for part in found[1].split(".")) if found else ()
        )
        dotted = bool(found and found[2])
        if level or (len(number) > 1 and dotted):
            yield paragraph, level, number, dotted


def _following(before: tuple[int, ...]) -> set[tuple[int, ...]]:
    return {
        (*before[:depth], before[depth] + 1) for depth in range(len(before))
    } | {(*before, 1)}


def _shown(number: tuple[int, ...]) -> str:
    return ".".join(str(part) for part in number)


@final
@dataclass(frozen=True, slots=True)
class Numbering(Check):
    """Clause 2.1.9: arabic numbers with a dot, running through a section."""

    document: Document
    rules: Catalog

    @override
    def violations(self) -> tuple[Violation, ...]:
        """Report numbers that break the run; titles without one restart it."""
        entries = tuple(_entries(self.document))
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
                        f"номер {_shown(number)} не продолжает нумерацию"
                        f" после {_shown(before)}"
                    )
                    if before
                    else f"номер {_shown(number)} вместо 1",
                    number not in _following(before),
                ),
                (
                    (
                        f"номер {('раздела', 'подраздела')[level - 1]}"
                        f" {_shown(number)} состоит не из"
                        f" {('одного числа', 'двух чисел')[level - 1]}"
                    ),
                    bool(level) and len(number) != level,
                ),
                (
                    f"после номера раздела {_shown(number)} нет точки",
                    level == 1 and not dotted,
                ),
            )
            if broken
        )
