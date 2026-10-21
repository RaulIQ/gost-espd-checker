"""The heads of the columns and rows of tables."""

import re
from dataclasses import dataclass
from typing import final

from docx.document import Document
from typing_extensions import override

from gost_espd_checker.catalog import Catalog
from gost_espd_checker.check import Check
from gost_espd_checker.label import Label
from gost_espd_checker.tables import Tables
from gost_espd_checker.violation import Violation


@final
@dataclass(frozen=True, slots=True)
class TableHeads(Check):
    """GOST 1.5-2001, clause 4.5.4: heads start with a capital, no period.

    Heads are the cells of the first row and the first cells of the other
    rows. A word in Latin letters, like a file name, keeps its own case,
    and a short word with a dot is taken for an abbreviation.
    """

    _document: Document
    _rules: Catalog

    @override
    def violations(self) -> tuple[Violation, ...]:
        """Report heads in a small Cyrillic letter or with a period."""
        return tuple(
            Violation(
                str(Label("таблица", caption, position + 1)),
                self._rules.rule("ESPD-015-03"),
                text,
            )
            for position, (table, caption, _) in enumerate(
                Tables(self._document)
            )
            for head in dict.fromkeys(
                cell.text.strip()
                for cell in (
                    *(table.rows[0].cells if table.rows else ()),
                    *(row.cells[0] for row in table.rows[1:] if row.cells),
                )
            )
            if head
            for text, broken in (
                (
                    f"первая буква заголовка «{head}» строчная",
                    bool(re.match(r"[\u0430-\u044f\u0451]", head)),
                ),
                (
                    f"в конце заголовка «{head}» стоит точка",
                    head.endswith(".")
                    and not re.search(r"(?<!\w)\w{1,5}\.$", head),
                ),
            )
            if broken
        )
