"""The inscription «Утвержден» on the title page of a document."""

import re
from dataclasses import dataclass
from typing import final

from docx.document import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from typing_extensions import override

from gost_espd_checker.catalog import Catalog
from gost_espd_checker.check import Check
from gost_espd_checker.effective import Effective
from gost_espd_checker.lineage import Lineage
from gost_espd_checker.title_page import TitlePage
from gost_espd_checker.violation import Violation


@final
@dataclass(frozen=True, slots=True)
class Endorsement(Check):
    """GOST 19.104-78, clause 3.2: «Утвержден» and the approval sheet."""

    _document: Document
    _rules: Catalog

    @override
    def violations(self) -> tuple[Violation, ...]:
        """Report a missing, misplaced or misspelt inscription."""
        lines = tuple(TitlePage(self._document))
        index = next(
            (
                position
                for position, line in enumerate(lines)
                if re.fullmatch(r"утвержд\w*", line.text.strip(), re.IGNORECASE)
            ),
            -1,
        )
        if index < 0:
            return (
                Violation(
                    "титульный лист",
                    self._rules.rule("ESPD-104-01"),
                    "на титульном листе нет надписи «Утвержден»",
                ),
            )
        word = lines[index].text.strip()
        return tuple(
            Violation("титульный лист", self._rules.rule("ESPD-104-01"), text)
            for designation in (
                "".join(
                    line.text.strip() for line in lines[index + 1 : index + 2]
                ),
            )
            for text, broken in (
                (
                    f"надпись «{word}» вместо «Утвержден»",
                    word.lower() != "утвержден",
                ),
                (
                    "надпись «Утвержден» стоит не в левом верхнем углу",
                    index > 0
                    or Effective(Lineage(lines[index])).alignment()
                    not in {
                        WD_PARAGRAPH_ALIGNMENT.LEFT,
                        WD_PARAGRAPH_ALIGNMENT.JUSTIFY,
                    },
                ),
                (
                    (
                        "под надписью «Утвержден» нет обозначения листа"
                        " утверждения"
                    ),
                    not re.match(r"\w+\.\S", designation),
                ),
                (
                    f"обозначение «{designation}» не оканчивается на «-ЛУ»",
                    bool(re.match(r"\w+\.\S", designation))
                    and not designation.endswith("-ЛУ"),
                ),
            )
            if broken
        )
