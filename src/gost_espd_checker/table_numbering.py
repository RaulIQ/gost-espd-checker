"""The numbers of the tables of a document."""

import re
from dataclasses import dataclass
from typing import final

from docx.document import Document
from typing_extensions import override

from gost_espd_checker.catalog import Catalog
from gost_espd_checker.check import Check
from gost_espd_checker.tables import Tables
from gost_espd_checker.violation import Violation


@final
@dataclass(frozen=True, slots=True)
class TableNumbering(Check):
    """GOST 1.5-2001, clause 4.5.3: tables run through the text in order.

    Tables of an appendix are numbered apart, after its designation and a
    dot. Numbers of the main text with a dot are numbers within a section,
    which the clause allows, and are left alone.
    """

    _document: Document
    _rules: Catalog

    @override
    def violations(self) -> tuple[Violation, ...]:
        """Report numbers that break the run of their part."""
        numbered = [
            (caption, appendix, found[1])
            for _, caption, appendix in Tables(self._document)
            for found in (
                re.match(r"таблица\s+([\w.]*\d)", caption, re.IGNORECASE),
            )
            if found
        ]
        return tuple(
            Violation(
                f"таблица «{caption}»",
                self._rules.rule("ESPD-015-02"),
                f"номер {number} вместо {expected}",
            )
            for position, (caption, appendix, number) in enumerate(numbered)
            for expected in (
                f"{appendix}." * bool(appendix)
                + str(
                    1
                    + sum(
                        1
                        for _, earlier, _ in numbered[:position]
                        if earlier == appendix
                    )
                ),
            )
            if number != expected and (appendix or "." not in number)
        )
