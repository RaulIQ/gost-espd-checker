"""The inscription «Утвержден» on the title page of a document."""

import re
from dataclasses import dataclass
from typing import final

from docx.document import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.text.paragraph import Paragraph
from typing_extensions import override

from gost_espd_checker.breaks import Breaks
from gost_espd_checker.check import Check
from gost_espd_checker.effective import Effective
from gost_espd_checker.rules import Catalog
from gost_espd_checker.violation import Violation


def _pages(document: Document) -> list[list[Paragraph]]:
    pages: list[list[Paragraph]] = [[]]
    for element in document.element.body.xpath(
        "./w:p | ./w:tbl[not(w:tblPr/w:tblpPr)]//w:p | ./w:sdt//w:p"
    ):
        paragraph = Paragraph(element, document)
        if pages[-1] and (
            Effective(paragraph).pagebreak() or Breaks(paragraph).opens()
        ):
            pages.append([])
        pages[-1].append(paragraph)
        if Breaks(paragraph).closes() or element.xpath("./w:pPr/w:sectPr"):
            pages.append([])
    return [page for page in pages if any(line.text.strip() for line in page)]


def _title(document: Document) -> list[Paragraph]:
    page = next(
        (
            page
            for page in _pages(document)
            if not any("лист утверждения" in line.text.lower() for line in page)
        ),
        [],
    )
    return [line for line in page if line.text.strip()]


@final
@dataclass(frozen=True, slots=True)
class Endorsement(Check):
    """GOST 19.104-78, clause 3.2: «Утвержден» and the approval sheet."""

    document: Document
    rules: Catalog

    @override
    def violations(self) -> tuple[Violation, ...]:
        """Report a missing, misplaced or misspelt inscription."""
        lines = _title(self.document)
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
                self._violation("на титульном листе нет надписи «Утвержден»"),
            )
        word = lines[index].text.strip()
        return tuple(
            self._violation(text)
            for text, broken in (
                (
                    f"надпись «{word}» вместо «Утвержден»",
                    word.lower() != "утвержден",
                ),
                (
                    "надпись «Утвержден» стоит не в левом верхнем углу",
                    index > 0
                    or Effective(lines[index]).alignment()
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
                    not "".join(
                        line.text.strip()
                        for line in lines[index + 1 : index + 2]
                    ).endswith("-ЛУ"),
                ),
            )
            if broken
        )

    def _violation(self, text: str) -> Violation:
        return Violation("титульный лист", self.rules.rule("ESPD-104-01"), text)
