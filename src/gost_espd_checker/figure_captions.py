"""Where the title and the number of an illustration stand."""

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
class FigureCaptions(Check):
    """Clause 2.3.1: the title goes over an illustration, the number under."""

    _document: Document
    _rules: Catalog

    @override
    def violations(self) -> tuple[Violation, ...]:
        """Report numbers over illustrations and titles beside numbers."""
        return tuple(
            Violation(
                f"иллюстрация «{caption}»",
                self._rules.rule("ESPD-106-20"),
                text,
            )
            for _, caption, above, _ in Illustrations(self._document)
            if caption
            for text, broken in (
                (
                    "номер стоит над иллюстрацией, хотя должен быть под ней",
                    above,
                ),
                (
                    (
                        "наименование записано в строке номера, хотя должно"
                        " быть над иллюстрацией"
                    ),
                    not re.fullmatch(
                        r"рис\.?\s*\d+\.?", caption, re.IGNORECASE
                    ),
                ),
            )
            if broken
        )
