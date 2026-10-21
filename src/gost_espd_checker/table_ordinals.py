"""The column of ordinal numbers in tables."""

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
class TableOrdinals(Check):
    """GOST 1.5-2001, clause 4.5.7: no column «Номер по порядку»."""

    document: Document
    rules: Catalog

    @override
    def violations(self) -> tuple[Violation, ...]:
        """Report heads like «№», «№ п/п» or «Номер по порядку»."""
        return tuple(
            Violation(
                str(Label("таблица", caption, position + 1)),
                self.rules.rule("ESPD-015-05"),
                f"в таблице есть графа «{head}»",
            )
            for position, (table, caption, _) in enumerate(
                Tables(self.document)
            )
            for head in dict.fromkeys(
                cell.text.strip() for cell in table.rows[0].cells if table.rows
            )
            if re.fullmatch(
                r"№(?:\s*п/?п)?|n\s*п/?п|номер по порядку|порядковый номер",
                head,
                re.IGNORECASE,
            )
        )
