"""The numbers of the illustrations of a document."""

import re
from dataclasses import dataclass
from typing import final

from docx.document import Document
from typing_extensions import override

from gost_espd_checker.catalog import Catalog
from gost_espd_checker.check import Check
from gost_espd_checker.illustrations import Illustrations
from gost_espd_checker.violation import Violation


@final
@dataclass(frozen=True, slots=True)
class FigureNumbering(Check):
    """Clause 2.3.1: illustrations are numbered in order, anew in appendices."""

    document: Document
    rules: Catalog

    @override
    def violations(self) -> tuple[Violation, ...]:
        """Report missing numbers and numbers out of order."""
        figures = tuple(Illustrations(self.document))
        numbers = [
            int(found[1]) if found else 0
            for _, caption, _, _ in figures
            for found in (re.match(r"рис\.?\s*(\d+)", caption, re.IGNORECASE),)
        ]
        expected = [
            max(
                (
                    numbers[earlier]
                    for earlier in range(position)
                    if figures[earlier][3] == figures[position][3]
                ),
                default=0,
            )
            + 1
            for position in range(len(figures))
        ]
        return tuple(
            Violation(
                f"иллюстрация «{caption}»"
                if caption
                else f"иллюстрация {position + 1} по порядку",
                self.rules.rule("ESPD-106-18"),
                text,
            )
            for position, (_, caption, _, _) in enumerate(figures)
            if len(figures) > 1
            for text, broken in (
                ("иллюстрация не пронумерована", not numbers[position]),
                (
                    f"номер {numbers[position]} вместо {expected[position]}",
                    numbers[position] not in {0, expected[position]},
                ),
            )
            if broken
        )
