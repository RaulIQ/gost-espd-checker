"""The letters of the names listed in the contents."""

import re
from dataclasses import dataclass
from typing import final

from docx.document import Document
from typing_extensions import override

from gost_espd_checker.catalog import Catalog
from gost_espd_checker.check import Check
from gost_espd_checker.records import Records
from gost_espd_checker.unnumbered import Unnumbered
from gost_espd_checker.violation import Violation


@final
@dataclass(frozen=True, slots=True)
class Lowercase(Check):
    """Clause 2.1.4: names in the contents are written in small letters."""

    _document: Document
    _rules: Catalog

    @override
    def violations(self) -> tuple[Violation, ...]:
        """Report names in capitals and names starting with a small letter."""
        return tuple(
            Violation("содержание", self._rules.rule("ESPD-106-28"), text)
            for record in Records(self._document)
            for letters in (
                "".join(re.findall(r"[^\W\d_]", str(Unnumbered(record)))),
            )
            for text, broken in (
                (
                    f"наименование «{record}» записано прописными буквами",
                    len(letters) > 1 and letters.isupper(),
                ),
                (
                    f"первая буква наименования «{record}» строчная",
                    letters[:1].islower(),
                ),
            )
            if broken
        )
